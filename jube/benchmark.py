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
"""The Benchmark class manages the benchmark process"""

import multiprocessing as mp
import xml.etree.ElementTree as ET
import xml.dom.minidom as DOM
import os
import re
import stat
import pprint
import shutil
import itertools
import jube.parameter
import jube.util.util
import jube.util.output
import jube.util.database_interface
import jube.conf
import jube.log

LOGGER = jube.log.get_logger(__name__)


class Benchmark(object):

    """The Benchmark class contains all data to run a benchmark"""

    def __init__(self, name, outpath, parametersets, substitutesets,
                 filesets, patternsets, steps, analyser, results,
                 results_order, comment="", tags=None, tag_docu=dict(),
                 file_path_ref=".", version=jube.conf.JUBE_VERSION):
        self._name = name
        self._outpath = outpath
        self._parametersets = parametersets
        self._substitutesets = substitutesets
        self._filesets = filesets
        self._patternsets = patternsets
        self._steps = steps
        self._analyser = analyser
        for analyser in self._analyser.values():
            analyser.benchmark = self
        self._results = results
        self._results_order = results_order
        for result in self._results.values():
            result.benchmark = self
        self._workpackages = dict()
        self._work_stat = jube.util.util.WorkStat()
        self._comment = comment
        self._id = -1
        self._file_path_ref = file_path_ref
        if tags is None:
            self._tags = set()
        else:
            self._tags = tags
        self._tag_docu = tag_docu
        self._db = None
        self._version = version

    @property
    def name(self):
        """Return benchmark name"""
        return self._name

    @property
    def outpath(self):
        """Return benchmark outpath"""
        return self._outpath
    
    @property
    def version(self):
        """Return benchmark JUBE version"""
        return self._version

    @property
    def comment(self):
        """Return comment string"""
        return self._comment

    @property
    def tags(self):
        """Return set of tags"""
        return self._tags

    @property
    def tag_docu(self):
        """Return dict of tag documentation"""
        return self._tag_docu

    @comment.setter
    def comment(self, new_comment):
        """Set new comment string"""
        self._comment = new_comment

    @property
    def parametersets(self):
        """Return parametersets"""
        return self._parametersets

    @property
    def patternsets(self):
        """Return patternsets"""
        return self._patternsets

    @property
    def analyser(self):
        """Return analyser"""
        return self._analyser

    @property
    def results(self):
        """Return results"""
        return self._results

    @property
    def results_order(self):
        """Return results_order"""
        return self._results_order

    @property
    def file_path_ref(self):
        """Get file path reference"""
        return self._file_path_ref

    @file_path_ref.setter
    def file_path_ref(self, file_path_ref):
        """Set file path reference"""
        self._file_path_ref = file_path_ref

    @property
    def substitutesets(self):
        """Return substitutesets"""
        return self._substitutesets

    @property
    def workpackages(self):
        """Return workpackages"""
        return self._workpackages

    def deinitialize_db(self):
        """Remove database instance"""
        if self._db:
            try:
                self._db.disconnect()
            except:
                pass
            self._db = None

    @property
    def db(self):
        """Return database instance"""
        if not self._db:
            self._db = jube.util.database_interface.Database_Interface(
                os.path.join(self.bench_dir, jube.conf.DATABASE_FILENAME))
        return self._db

    def add_tags(self, other_tags):
        if other_tags is not None:
            self._tags = self._tags.union(set(other_tags))

    def workpackage_by_id(self, wp_id):
        """Search and return a benchmark workpackage by its wp_id"""
        for stepname in self._workpackages:
            for workpackage in self._workpackages[stepname]:
                if workpackage.id == wp_id:
                    return workpackage
        return None

    def remove_workpackage(self, workpackage_to_delete):
        """Remove a specific workpackage"""
        stepname = workpackage_to_delete.step.name
        if stepname in self._workpackages and \
                workpackage_to_delete in self._workpackages[stepname]:
            self._workpackages[stepname].remove(workpackage_to_delete)
            self._remove_workpackage_from_database(workpackage_to_delete)

    def _remove_workpackage_from_database(self, workpackage_to_delete):
        """Remove a specific workpackage from database"""
        # Get database instance and connect
        self.db.connect()
        try:
            self.db.start_transaction()
            #deletes workpackage and any depend data in other tables
            self.db.delete("Workpackage", f"workpackage_id='{workpackage_to_delete.id}'")
            self.db.commit_transaction()
        except Exception as e:
            LOGGER.warning(str(e))
            self.db.rollback_transaction()
            self.db.disconnect()
            raise e
        self.db.disconnect()

    @property
    def work_stat(self):
        """Return work queue"""
        return self._work_stat

    @property
    def filesets(self):
        """Return filesets"""
        return self._filesets

    def delete_bench_dir(self):
        """Delete all data inside benchmark directory"""
        if os.path.exists(self.bench_dir):
            shutil.rmtree(self.bench_dir, ignore_errors=True)

    def delete_xml_configuration(self):
        """Delete configuration.xml"""
        # DEPRECATED (Full function): Future versions will no longer support XML files
        xml_configuration = os.path.join(self.bench_dir, jube.conf.CONFIGURATION_FILENAME)
        if os.path.exists(xml_configuration):
            os.remove(xml_configuration)

    def delete_xml_workpackages(self):
        """Delete workpackages.xml"""
        # DEPRECATED (Full function): Future versions will no longer support XML files
        xml_workpackages = os.path.join(self.bench_dir, jube.conf.WORKPACKAGES_FILENAME)
        if os.path.exists(xml_workpackages):
            os.remove(xml_workpackages)

    @property
    def steps(self):
        """Return steps"""
        return self._steps

    @property
    def workpackage_status(self):
        """Return workpackage information dict"""
        result_dict = dict()
        for stepname in self._workpackages:
            result_dict[stepname] = {"all": 0,
                                     "open": 0,
                                     "wait": 0,
                                     "error": 0,
                                     "done": 0}
            for workpackage in self._workpackages[stepname]:
                result_dict[stepname]["all"] += 1
                if workpackage.status == "done_debug":
                    if jube.conf.DEBUG_MODE:
                        result_dict[stepname]["done"] += 1
                    else:
                        result_dict[stepname]["open"] += 1
                else:
                    result_dict[stepname][workpackage.status] += 1
        return result_dict

    @property
    def benchmark_status(self):
        """Return global workpackage information dict"""
        result_dict = {"all": 0,
                       "open": 0,
                       "wait": 0,
                       "error": 0,
                       "done": 0}

        for status in self.workpackage_status.values():
            result_dict["all"] += status["all"]
            result_dict["open"] += status["open"]
            result_dict["wait"] += status["wait"]
            result_dict["error"] += status["error"]
            result_dict["done"] += status["done"]

        return result_dict

    @property
    def id(self):
        """Return benchmark id"""
        return self._id

    @id.setter
    def id(self, new_id):
        """Set new benchmark id"""
        self._id = new_id

    def get_jube_parameterset(self):
        """Return parameterset which contains benchmark related
        information"""
        parameterset = jube.parameter.Parameterset()
        # benchmark id
        parameterset.add_parameter(
            jube.parameter.Parameter.
            create_parameter(
                "jube_benchmark_id", str(self._id), parameter_type="int",
                update_mode=jube.parameter.JUBE_MODE))

        # benchmark id with padding
        parameterset.add_parameter(
            jube.parameter.Parameter.
            create_parameter("jube_benchmark_padid",
                             jube.util.util.id_dir("", self._id),
                             parameter_type="string",
                             update_mode=jube.parameter.JUBE_MODE))

        # benchmark name
        parameterset.add_parameter(
            jube.parameter.Parameter.
            create_parameter("jube_benchmark_name", self._name,
                             update_mode=jube.parameter.JUBE_MODE))

        # benchmark home
        parameterset.add_parameter(
            jube.parameter.Parameter.
            create_parameter("jube_benchmark_home",
                             os.path.abspath(self._file_path_ref),
                             update_mode=jube.parameter.JUBE_MODE))

        # benchmark rundir
        parameterset.add_parameter(
            jube.parameter.Parameter.
            create_parameter("jube_benchmark_rundir",
                             os.path.abspath(self.bench_dir),
                             update_mode=jube.parameter.JUBE_MODE))

        timestamps = jube.util.util.read_timestamps(
            os.path.join(self.bench_dir, jube.conf.TIMESTAMPS_INFO))

        # benchmark start
        parameterset.add_parameter(
            jube.parameter.Parameter.create_parameter(
                "jube_benchmark_start",
                timestamps.get("start", "").replace(" ", "T"),
                update_mode=jube.parameter.JUBE_MODE))

        return parameterset

    def __repr__(self):
        return pprint.pformat(self.__dict__)

    def _create_initial_workpackages(self):
        """Create initial workpackages of current benchmark and create graph
        structure."""
        self._workpackages = dict()
        self._work_stat = jube.util.util.WorkStat()

        # Create workpackage storage
        for step_name in self._steps:
            self._workpackages[step_name] = list()

        # Create initial workpackages
        for step in self._steps.values():
            if len(step.depend) == 0:
                new_workpackages = \
                    self._create_new_workpackages_with_parents(step)
                self._workpackages[step.name] += new_workpackages
                for workpackage in new_workpackages:
                    workpackage.queued = True
                    self._work_stat.put(workpackage)

    def analyse(self, show_info=True, specific_analyser_name=None):
        """Run analyser"""

        if show_info:
            LOGGER.info(">>> Start analyse")

        if specific_analyser_name is not None and \
                specific_analyser_name in self._analyser:
            self._analyser[specific_analyser_name].analyse()
        else:
            for analyser in self._analyser.values():
                analyser.analyse()
        if ((not jube.conf.DEBUG_MODE) and
                (os.access(self.bench_dir, os.W_OK))):
            self.write_analyse_data(os.path.join(self.bench_dir,
                                                 jube.conf.ANALYSE_FILENAME))
        if show_info:
            LOGGER.info(">>> Analyse finished")

    def create_result(self, only=None, show=False, data_list=None, style=None,
                      select=None, exclude=None):
        """Show benchmark result"""
        if only is None:
            only = [result_name for result_name in self._results]
        if data_list is None:
            data_list = list()
        for result_name in self._results_order:
            result = self._results[result_name]
            if result.name in only:
                result_data = result.create_result_data(style, select, exclude)
                if result.result_dir is None:
                    result_dir = os.path.join(self.bench_dir,
                                              jube.conf.RESULT_DIRNAME)
                else:
                    result_dir = result.result_dir
                    result_dir = os.path.expanduser(result_dir)
                    result_dir = os.path.expandvars(result_dir)
                    result_dir = jube.util.util.id_dir(
                        os.path.join(self.file_path_ref, result_dir), self.id)
                if (not os.path.exists(result_dir)) and \
                   (not jube.conf.DEBUG_MODE):
                    try:
                        os.makedirs(result_dir)
                    except OSError:
                        pass
                if ((not jube.conf.DEBUG_MODE) and
                        (os.path.exists(result_dir)) and
                        (os.access(result_dir, os.W_OK))):
                    filename = os.path.join(result_dir,
                                            "{0}.dat".format(result.name))
                else:
                    filename = None
                result_data.create_result(show=show, filename=filename)

                if result_data in data_list:
                    data_list[data_list.index(result_data)].add_result_data(
                        result_data)
                else:
                    data_list.append(result_data)
        return data_list

    def update_analyse_and_result(self, new_patternsets, new_analyser,
                                  new_results, new_results_order, new_cwd):
        """Update analyser and result data"""
        if os.path.exists(self.bench_dir):
            LOGGER.debug("Update analyse and result data")
            self._patternsets = new_patternsets
            old_analyser = self._analyser
            self._analyser = new_analyser
            self._results = new_results
            self._results_order = new_results_order
            for analyser in self._analyser.values():
                if analyser.name in old_analyser:
                    analyser.analyse_result = \
                        old_analyser[analyser.name].analyse_result
                analyser.benchmark = self
            for result in self._results.values():
                result.benchmark = self
                # change result dir position relative to cwd
                if (result.result_dir is not None) and \
                   (new_cwd is not None) and \
                   (not os.path.isabs(result.result_dir)):
                    result.result_dir = \
                        os.path.join(new_cwd, result.result_dir)
            if ((not jube.conf.DEBUG_MODE) and
                    (os.access(self.bench_dir, os.W_OK))):
                self.update_benchmark_configuration_in_database()

    def write_analyse_data(self, filename):
        """All analyse data will be written to given file
        using xml representation"""
        # Create root-tag and append analyser
        analyse_etree = ET.Element("analyse")
        for analyser_name in self._analyser:
            analyser_etree = ET.SubElement(analyse_etree, "analyser")
            analyser_etree.attrib["name"] = analyser_name
            for etree in self._analyser[analyser_name].analyse_etree_repr():
                analyser_etree.append(etree)
        xml = jube.util.output.element_tree_tostring(
            analyse_etree, encoding="UTF-8")
        # Using dom for pretty-print
        dom = DOM.parseString(xml.encode("UTF-8"))
        fout = open(filename, "wb")
        fout.write(dom.toprettyxml(indent="  ", encoding="UTF-8"))
        fout.close()

    def _create_new_workpackages_for_workpackage(self, workpackage):
        """Create and return new workpackages if given workpackage
        was finished."""
        all_new_workpackages = list()
        if not workpackage.done or len(workpackage.children) > 0:
            return all_new_workpackages
        LOGGER.debug(("Create new workpackages for workpackage"
                      " {0}({1})").format(
            workpackage.step.name, workpackage.id))
        # Search for dependent steps
        dependent_steps = [step for step in self._steps.values() if
                           workpackage.step.name in step.depend]

        # Search for possible workpackage parents
        for dependent_step in dependent_steps:
            parent_workpackages = [[
                parent_workpackage for parent_workpackage in
                self._workpackages[step_name] if parent_workpackage.done]
                for step_name in dependent_step.depend
                if (step_name in self._workpackages) and
                   (step_name != workpackage.step.name)]
            parent_workpackages.append([workpackage])

            # Create all possible parent combinations
            workpackage_combinations = \
                [iterator for iterator in
                 itertools.product(*parent_workpackages)]
            possible_combination = len(workpackage_combinations)
            for workpackage_combination in workpackage_combinations:
                new_workpackages = self._create_new_workpackages_with_parents(
                    dependent_step, workpackage_combination)
                if len(new_workpackages) > 0:
                    possible_combination -= 1

                # Create links: parent workpackages -> new children
                for new_workpackage in new_workpackages:
                    for parent in workpackage_combination:
                        parent.add_children(new_workpackage)

                self._workpackages[dependent_step.name] += new_workpackages
                all_new_workpackages += new_workpackages
            if possible_combination > 0:
                LOGGER.debug(("  {0} workpackages combinations were skipped"
                              " while checking possible parent combinations"
                              " for step {1}").format(possible_combination,
                                                      dependent_step.name))

        LOGGER.debug("  {0} new workpackages created".format(
            len(all_new_workpackages)))
        return all_new_workpackages

    def _create_new_workpackages_with_parents(self, step,
                                              parent_workpackages=None):
        """Create workpackages with given parent combination"""
        if parent_workpackages is None:
            parent_workpackages = list()
        # Combine and check parent parametersets
        parameterset = jube.parameter.Parameterset()
        incompatible_parameter_names = set()
        for parent_workpackage in parent_workpackages:
            # Check weather parameter combination is possible or not.
            # JUBE Parameter can be ignored
            incompatible_parameter_names = incompatible_parameter_names.union(
                parameterset.get_incompatible_parameter(
                    parent_workpackage.parameterset,
                    update_mode=jube.parameter.JUBE_MODE))
            parameterset.add_parameterset(
                parent_workpackage.parameterset)

        # Sort parent workpackages after total iteration number and name
        sorted_parents = list(parent_workpackages)
        sorted_parents.sort(key=lambda x: x.step.name)
        sorted_parents.sort(key=lambda x: x.step.iterations)

        iteration_base = 0
        for i, parent in enumerate(sorted_parents):
            if i == 0:
                iteration_base = parent.iteration
            else:
                iteration_base = \
                    parent.step.iterations * iteration_base + parent.iteration

        parameterset.remove_jube_parameter()

        # Create new workpackages
        new_workpackages = step.create_workpackages(
            self, parameterset,
            iteration_base=iteration_base,
            parents=parent_workpackages,
            incompatible_parameters=incompatible_parameter_names)

        # Update iteration sibling connections
        if len(parent_workpackages) > 0 and len(new_workpackages) > 0:
            for sibling in parent_workpackages[0].iteration_siblings:
                if sibling != parent_workpackages[0]:
                    for child in sibling.children:
                        for workpackage in new_workpackages:
                            if workpackage.parameterset.is_compatible(
                                    child.parameterset,
                                    update_mode=jube.parameter.JUBE_MODE):
                                workpackage.iteration_siblings.add(child)
                                child.iteration_siblings.add(workpackage)

        return new_workpackages

    def new_run(self):
        """Create workpackage structure and run benchmark"""
        # Check benchmark consistency
        LOGGER.debug("Start consistency check")
        jube.util.util.consistency_check(self)

        # Create benchmark directory
        LOGGER.debug("Create benchmark directory")
        self._create_bench_dir()

        # Change logfile
        jube.log.change_logfile_name(os.path.join(
            self.bench_dir, jube.conf.LOGFILE_RUN_NAME))
        # Move parse logfile into benchmark folder
        if os.path.isfile(os.path.join(self._file_path_ref,
                                       jube.conf.DEFAULT_LOGFILE_NAME)):
            shutil.move(os.path.join(self._file_path_ref,
                                     jube.conf.DEFAULT_LOGFILE_NAME),
                        os.path.join(self.bench_dir,
                                     jube.conf.LOGFILE_PARSE_NAME))

        # Reset Workpackage counter
        jube.workpackage.Workpackage.id_counter = 0

        # Create initial workpackages
        LOGGER.debug("Create initial workpackages")
        self._create_initial_workpackages()

        # Store workpackage information
        LOGGER.debug("Store initial workpackage information")
        self.add_workpackage_information_to_database()

        LOGGER.debug("Start benchmark run")

        self.run()

    def run(self):
        """Run benchmark"""
        title = "benchmark: {0}".format(self._name)
        title += "\nid: {0}".format(self._id)
        if jube.conf.DEBUG_MODE:
            title += " ---DEBUG_MODE---"
        title += "\n\n{0}".format(self._comment)
        infostr = jube.util.output.text_boxed(title)
        LOGGER.info(infostr)

        if not jube.conf.HIDE_ANIMATIONS:
            print("\nRunning workpackages (#=done, 0=wait, E=error):")
            status = self.benchmark_status
            jube.util.output.print_loading_bar(
                status["done"], status["all"], status["wait"], status["error"])

        # Handle all workpackages in given order
        while not self._work_stat.empty():
            workpackage = self._work_stat.get()

            run_parallel = False

            def collect_result(val):
                """used collect return values from pool.apply_async"""
                # run postprocessing of each wp
                for i, wp in enumerate(self._workpackages[val["step_name"]]):
                    if wp.id == val["id"]:
                        if(len(val) == 2):  # workpackage is done or its execution was erroneous
                            pass
                        else:
                            # update corresponding wp in self._workpackage with modified wp
                            wp.env = val["env"]
                            # restore the parameters containing a method of a class,
                            # which needed to be deleted within the multiprocess
                            # execution to avoid excessive memory usage
                            for p in wp._parameterset.all_parameters:
                                if(p.search_method(propertyString="eval_helper",
                                                   recursiveProperty="based_on")):
                                    val["parameterset"].add_parameter(p)
                            wp.parameterset = val["parameterset"]
                            wp.cycle = val["cycle"]
                            wp.status = val["status"]
                        self.wp_post_run_config(wp)
                        break

            def log_e(e):
                """used to print error_callback from pool.apply_async"""
                print(e)

            if not workpackage.done:
                # execute wps in parallel which have the same name
                if workpackage.step.procs > 1:
                    #Remove database instance to run parallel
                    self.deinitialize_db()

                    run_parallel = True
                    procs = workpackage.step.procs
                    name = workpackage.step.name
                    pool = mp.Pool(processes=procs)

                    # save current logfile name to restore logs in the right logfile
                    current_logfile_name = jube.log.LOGFILE_NAME

                    # add wps to the parallel pool as long as they have the same name
                    while True:
                        pool.apply_async(workpackage.run, args=('p',),
                                         callback=collect_result, error_callback=log_e)

                        if not self._work_stat.empty():
                            workpackage = self._work_stat.get()
                            # push back as first element of _work_stat and
                            # terminate parallel loop
                            if workpackage.step.name != name:
                                self._work_stat.push_back(workpackage)
                                break
                        else:
                            break

                    pool.close()
                    pool.join()
                else:
                    workpackage.run()

            if run_parallel:
                # merge parallel run log files into the main run log file and
                # delete the parallel logs
                log_fname = jube.log.LOGFILE_NAME.split('/')[-1]
                filenames = [file for file in os.listdir(self.bench_dir)
                             if file.startswith(log_fname.split('.')[0]) and
                             file != log_fname]
                filenames.sort(key=lambda o: int(re.split(r'_|\.', o)[1]))
                with open(current_logfile_name, 'a') as outfile:
                    for fname in filenames:
                        with open(os.path.join(self.bench_dir, fname), 'r') as infile:
                            contents = infile.read()
                            outfile.write(contents)
                        os.remove(os.path.join(self.bench_dir, fname))

                run_parallel = False
            else:
                self.wp_post_run_config(workpackage)

        self.add_workpackage_information_to_database()

        print("\n")
        status_data = [("stepname", "all", "open", "wait", "error", "done")]
        status_data += [(stepname, str(_status["all"]), str(_status["open"]),
                         str(_status["wait"]), str(_status["error"]),
                         str(_status["done"]))
                        for stepname, _status in
                        self.workpackage_status.items()]
        LOGGER.info(jube.util.output.text_table(
            status_data, use_header_line=True, indent=2))

        LOGGER.info("\n>>>> Benchmark information and " +
                    "further useful commands:")
        LOGGER.info(">>>>       id: {0}".format(self._id))
        LOGGER.info(">>>>   handle: {0}".format(self._outpath))
        LOGGER.info(">>>>      dir: {0}".format(self.bench_dir))

        status = self.benchmark_status
        if status["all"] != status["done"]:
            LOGGER.info((">>>> continue: jube continue {0} " +
                         "--id {1}").format(self._outpath, self._id))
        LOGGER.info((">>>>  analyse: jube analyse {0} " +
                     "--id {1}").format(self._outpath, self._id))
        LOGGER.info((">>>>   result: jube result {0} " +
                     "--id {1}").format(self._outpath, self._id))
        LOGGER.info((">>>>     info: jube info {0} " +
                     "--id {1}").format(self._outpath, self._id))
        LOGGER.info((">>>>      log: jube log {0} " +
                     "--id {1}").format(self._outpath, self._id))
        LOGGER.info(jube.util.output.text_line() + "\n")

    def wp_post_run_config(self, workpackage):
        """additional processing of workpackage:
        - update status bar
        - build up queue after restart
        """
        self._create_new_workpackages_for_workpackage(workpackage)

        # Update queues (move waiting workpackages to work queue
        # if possible)
        self._work_stat.update_queues(workpackage)

        #Update workpackage status for jube parameter
        workpackage.update_status()

        if not jube.conf.HIDE_ANIMATIONS:
            status = self.benchmark_status
            jube.util.output.print_loading_bar(
                status["done"], status["all"], status["wait"],
                status["error"])
        workpackage.queued = False

        for mode in ("only_started", "all"):
            for child in workpackage.children:
                all_done = True
                for parent in child.parents:
                    all_done = all_done and parent.done
                if all_done:
                    if (mode == "only_started" and child.started) or \
                            (mode == "all" and (not child.queued)):
                        child.queued = True
                        self._work_stat.put(child)

    def _create_bench_dir(self):
        """Create the directory for a benchmark."""
        # Get group_id if available (given by JUBE_GROUP_NAME)
        group_id = jube.util.util.check_and_get_group_id()
        # Check if outpath exists
        if not (os.path.exists(self._outpath) and
                os.path.isdir(self._outpath)):
            os.makedirs(self._outpath)
            if group_id is not None:
                os.chown(self._outpath, os.getuid(), group_id)
        # Generate unique ID in outpath
        if self._id < 0:
            self._id = jube.util.util.get_current_id(self._outpath) + 1
        if os.path.exists(self.bench_dir):
            raise RuntimeError("Benchmark directory \"{0}\" already exists"
                               .format(self.bench_dir))

        os.makedirs(self.bench_dir)
        # If JUBE_GROUP_NAME is given, set GID-Bit and change group
        if group_id is not None:
            os.chown(self.bench_dir, os.getuid(), group_id)
            os.chmod(self.bench_dir,
                     os.stat(self.bench_dir).st_mode | stat.S_ISGID)

        self.add_benchmark_configuration_to_database(outpath="..")
        jube.util.util.update_timestamps(os.path.join(
            self.bench_dir, jube.conf.TIMESTAMPS_INFO), "start", "change")

    def add_benchmark_configuration_to_database(self, outpath=None):
        """Store benchmark configuration in database"""
        self.db.connect()
        self.db.create_database()

        try:
            self.db.start_transaction()
            benchmark_data = {
                "benchmark_id": self._id,
                "version": jube.conf.JUBE_VERSION,
                "name": self._name,
                "file_path_ref": os.path.relpath(self._file_path_ref, self.bench_dir)
            }
            if outpath is not None:
                benchmark_data["outpath"] = outpath
            if len(self._comment) > 0:
                benchmark_data["comment"] = self._comment
            self.db.insert("Benchmark", benchmark_data)

            if len(self._tags) > 0:
                for tag in self._tags:
                    self.db.insert("Tag", {"value": tag, "benchmark_id": self._id})
            if len(self._tag_docu) > 0:
                for tag, docu in self._tag_docu.items():
                    self.db.insert("TagDocu", {"tag": tag, "description": docu,
                                               "benchmark_id": self._id})
            self.db.commit_transaction()
        except Exception as e:
            LOGGER.warning(str(e))
            self.db.rollback_transaction()
            self.db.disconnect()
            raise e

        for parameterset in self._parametersets.values():
            parameterset.add_information_to_database(self.db, self._id)
        for substituteset in self._substitutesets.values():
            substituteset.add_information_to_database(self.db, self._id)
        for fileset in self._filesets.values():
            fileset.add_information_to_database(self.db, self._id)
        for patternset in self._patternsets.values():
            patternset.add_information_to_database(self.db, self._id)
        for step in self._steps.values():
            step.add_information_to_database(self.db, self._id)
            step.add_used_sets_to_database(self.db, self, {})
        for analyser in self._analyser.values():
            analyser.add_information_to_database(self.db, self._id)
        for result_name in self._results_order:
            result = self._results[result_name]
            result.add_information_to_database(self.db, self._id)
        self.db.disconnect()

    def update_benchmark_configuration_in_database(self):
        """Update benchmark configuration in database"""
        self.db.connect()
        # Update patternsets in database
        for patternset in self._patternsets.values():
            patternset.add_information_to_database(self.db, self._id, update=True)
        # Update analyser in database
        for analyser in self._analyser.values():
            analyser.add_information_to_database(self.db, self._id, update=True)
        # Update results in database
        for result_name in self._results_order:
            result = self._results[result_name]
            result.add_information_to_database(self.db, self._id, update=True)
        self.db.disconnect()

    def update_benchmark_comment_in_database(self):
        """Update benchmark comment in database"""
        self.db.connect()
        try:
            self.db.start_transaction()
            benchmark_data = {
                "comment": self._comment
            }
            self.db.update("Benchmark", {"comment": self._comment},
                             f"benchmark_id='{self._id}'")
            self.db.commit_transaction()
        except Exception as e:
            LOGGER.warning(str(e))
            self.db.rollback_transaction()
            self.db.disconnect()
            raise e
        self.db.disconnect()

    def reset_all_workpackages(self):
        """Reset workpackage state"""
        for workpackages in self._workpackages.values():
            for workpackage in workpackages:
                workpackage.done = False

    def add_workpackage_information_to_database(self):
        """Store initial workpackage information in database"""
        self.db.connect()
        for workpackages in self._workpackages.values():
            for workpackage in workpackages:
                row = self.db.select("Workpackage", condition=f"workpackage_id='{workpackage.id}'")
                if not row:
                    workpackage.add_information_to_database(self.db)
        self.db.disconnect()

    def set_workpackage_information(self, workpackages, work_stat):
        """Set new workpackage information"""
        self._workpackages = workpackages
        self._work_stat = work_stat

    @property
    def bench_dir(self):
        """Return benchmark directory"""
        return jube.util.util.id_dir(self._outpath, self._id)
