# JUBE Benchmarking Environment
# Copyright (C) 2008-2024
# Forschungszentrum Juelich GmbH, Juelich Supercomputing Centre
# http://www.fz-juelich.de/jsc/jube
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""Fileset related classes"""

from __future__ import (print_function,
                        unicode_literals,
                        division)

import os
import shutil
import jube.util.util
import jube.conf
import jube.step
import jube.log
import glob

LOGGER = jube.log.get_logger(__name__)


class Fileset(list):

    """Container for file copy, link and prepare operations"""

    def __init__(self, name):
        list.__init__(self)
        self._name = name

    @property
    def name(self):
        """Return fileset name"""
        return self._name

    def add_information_to_database(self, db, benchmark_id):
        """Store fileset information in database"""
        try:
            db.start_transaction()
            set_data = {
                "fileset_name": self._name,
                "benchmark_id": benchmark_id
            }
            db.insert("Fileset", set_data)
            for file_handle in self:
                file_handle.add_information_to_database(db, self._name)
            db.commit_transaction()
        except Exception as e:
            LOGGER.warning(str(e))
            db.rollback_transaction()
            db.disconnect()
            raise e

    def create(self, work_dir, parameter_dict, alt_work_dir=None,
               environment=None, file_path_ref=""):
        """Copy/load/prepare all files in fileset"""
        for file_handle in self:
            if type(file_handle) is Prepare:
                file_handle.execute(
                    parameter_dict=parameter_dict,
                    work_dir=alt_work_dir if alt_work_dir
                    is not None else work_dir,
                    environment=environment)
            else:
                file_handle.create(
                    work_dir=work_dir, parameter_dict=parameter_dict,
                    alt_work_dir=alt_work_dir, file_path_ref=file_path_ref,
                    environment=environment)


class File(object):

    """Generic file access"""

    def __init__(self, path, name=None, is_internal_ref=False, active="true",
                 source_dir="", target_dir=""):
        self._path = path
        self._source_dir = source_dir
        self._target_dir = target_dir
        self._name = name
        self._file_path_ref = ""
        self._active = active
        self._is_internal_ref = is_internal_ref

    @property
    def file_type(self):
        """Return file type"""
        return type(self).__name__

    @property
    def path(self):
        """Return file path"""
        return self._path

    @property
    def source_dir(self):
        """Return file source dir"""
        return self._source_dir

    @property
    def target_dir(self):
        """Return file source dir"""
        return self._target_dir

    @property
    def active(self):
        """Return file active status"""
        return self._active

    def create(self, work_dir, parameter_dict, alt_work_dir=None,
               file_path_ref="", environment=None):
        """Create file access"""
        # Check active status
        active = jube.util.util.eval_bool(jube.util.util.substitution(
            self._active, parameter_dict))
        if not active:
            return
        pathname = jube.util.util.substitution(self._path, parameter_dict)
        pathname = os.path.expanduser(pathname)
        source_dir = jube.util.util.substitution(self._source_dir,
                                                  parameter_dict)
        source_dir = os.path.expanduser(source_dir)
        target_dir = jube.util.util.substitution(self._target_dir,
                                                  parameter_dict)
        target_dir = os.path.expanduser(target_dir)
        if environment is not None:
            pathname = jube.util.util.substitution(pathname, environment)
            source_dir = jube.util.util.substitution(source_dir, environment)
            target_dir = jube.util.util.substitution(target_dir, environment)
        else:
            pathname = os.path.expandvars(pathname)
            source_dir = os.path.expandvars(source_dir)
            target_dir = os.path.expandvars(target_dir)

        # Add source prefix directory if needed
        pathname = os.path.join(source_dir, pathname)

        if self._is_internal_ref:
            pathname = os.path.join(work_dir, pathname)
        else:
            pathname = os.path.join(self._file_path_ref, pathname)
            pathname = os.path.join(file_path_ref, pathname)
            pathname = os.path.normpath(pathname)
        if self._name is None:
            name = os.path.basename(pathname)
        else:
            name = jube.util.util.substitution(self._name, parameter_dict)
            name = os.path.expanduser(name)
            if environment is not None:
                name = jube.util.util.substitution(name, environment)
            else:
                name = os.path.expandvars(name)

        if alt_work_dir is not None:
            work_dir = alt_work_dir
        # Shell expansion
        paths = glob.glob(pathname)
        if (len(paths) == 0) and (not jube.conf.DEBUG_MODE):
            raise RuntimeError("no files found using \"{0}\""
                               .format(pathname))
        for path in paths:
            # When using shell extensions, alternative filenames are not
            # allowed for multiple matches.
            if (len(paths) > 1) or ((pathname != path) and
                                     (name == os.path.basename(pathname))):
                name = os.path.basename(path)

            # Add target prefix directory if needed
            name = os.path.join(target_dir, name)

            new_file_path = os.path.join(work_dir, name)

            # Create target_dir if needed
            if (len(os.path.dirname(new_file_path)) > 0 and
                    not os.path.exists(os.path.dirname(new_file_path)) and
                    not jube.conf.DEBUG_MODE):
                os.makedirs(os.path.dirname(new_file_path))

            self.create_action(path, name, new_file_path)

    def create_action(self, path, name, new_file_path):
        """File access type specific creation"""
        raise NotImplementedError()

    def add_information_to_database(self, db, fileset_name):
        """Store file information in database"""
        raise NotImplementedError()

    @property
    def path(self):
        """Return filepath"""
        return self._path

    @property
    def file_path_ref(self):
        """Get file path reference"""
        return self._file_path_ref

    @file_path_ref.setter
    def file_path_ref(self, file_path_ref):
        """Set file path reference"""
        self._file_path_ref = file_path_ref

    @property
    def is_internal_ref(self):
        """Return path is internal ref"""
        return self._is_internal_ref
    
    @property
    def source_dir(self):
        """Return source directory"""
        return self._source_dir
    
    @property
    def target_dir(self):
        """Return target directory"""
        return self._target_dir
    
    @property
    def name(self):
        """Return alternative name"""
        return self._name
    
    @property
    def active(self):
        """Return active"""
        return self._active

    def __repr__(self):
        return self._path


class Link(File):

    """A link to a given path. Which can be used inside steps."""

    def create_action(self, path, name, new_file_path):
        """Create link to file in work_dir"""
        # Manipulate target_path if a new relative name path was selected
        if os.path.isabs(path):
            target_path = path
        else:
            target_path = os.path.relpath(path, os.path.dirname(new_file_path))
        LOGGER.debug("  link \"{0}\" <- \"{1}\"".format(target_path, name))
        if not jube.conf.DEBUG_MODE and not os.path.exists(new_file_path):
            os.symlink(target_path, new_file_path)

    def add_information_to_database(self, db, fileset_name):
        """Store link information in database"""
        file_data = {
            "path": self._path,
            "fileset_name": fileset_name,
            "type": "Link",
        }
        if self._name is not None:
            file_data["name"] = self._name
        if self._active != "true":
            file_data["active"] = self._active
        if self._source_dir != "":
            file_data["source_dir"] = self._source_dir
        if self._target_dir != "":
            file_data["target_dir"] = self._target_dir
        if self._file_path_ref != "":
            file_data["file_path_ref"] = self._file_path_ref
        if self._is_internal_ref:
            file_data["is_internal_ref"] = 1
        return db.insert("File", file_data)


class Copy(File):

    """A file or directory given by path. Which can be copied to the work_dir
    inside steps.
    """

    def create_action(self, path, name, new_file_path):
        """Copy file/directory to work_dir"""
        LOGGER.debug("  copy \"{0}\" -> \"{1}\"".format(path, name))
        if not jube.conf.DEBUG_MODE and not os.path.exists(new_file_path):
            if os.path.isdir(path):
                shutil.copytree(path, new_file_path, symlinks=True)
            else:
                shutil.copy2(path, new_file_path)

    def add_information_to_database(self, db, fileset_name):
        """Store copy information in database"""
        file_data = {
            "path": self._path,
            "fileset_name": fileset_name,
            "type": "Copy"
        }
        if self._name is not None:
            file_data["name"] = self._name
        if self._active != "true":
            file_data["active"] = self._active
        if self._source_dir != "":
            file_data["source_dir"] = self._source_dir
        if self._target_dir != "":
            file_data["target_dir"] = self._target_dir
        if self._file_path_ref != "":
            file_data["file_path_ref"] = self._file_path_ref
        if self._is_internal_ref:
            file_data["is_internal_ref"] = 1
        return db.insert("File", file_data)


class Prepare(jube.step.Operation):

    """Prepare the workpackage work directory"""

    def __init__(self, cmd, stdout_filename=None, stderr_filename=None,
                 work_dir=None, active="true"):
        jube.step.Operation.__init__(self,
                                      do=cmd,
                                      stdout_filename=stdout_filename,
                                      stderr_filename=stderr_filename,
                                      active=active,
                                      work_dir=work_dir)

    def execute(self, parameter_dict, work_dir, only_check_pending=False,
                environment=None):
        """Execute the prepare command"""
        jube.step.Operation.execute(
            self, parameter_dict=parameter_dict, work_dir=work_dir,
            only_check_pending=only_check_pending, environment=environment)

    def add_information_to_database(self, db, fileset_name):
        """Store prepare information in database"""
        do_data = {
            "do": self._do,
            "fileset_name": fileset_name
        }
        if self._stdout_filename is not None:
            do_data["stdout"] = self._stdout_filename
        if self._stderr_filename is not None:
            do_data["stderr"] = self._stderr_filename
        if self._active != "true":
            step_data["active"] = self._active
        if self._work_dir is not None:
            do_data["work_dir"] = self._work_dir
        db.insert("Prepare", do_data)
