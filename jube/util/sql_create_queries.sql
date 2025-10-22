-- sql_create_queries.sql

-- Table Benchmark
CREATE TABLE IF NOT EXISTS Benchmark
(
    benchmark_id INTEGER NOT NULL PRIMARY KEY,
    name TEXT NOT NULL,
    comment TEXT DEFAULT "" NOT NULL,
    outpath TEXT,
    version TEXT NOT NULL,
    file_path_ref TEXT NOT NULL
);

-- Table Tag
CREATE TABLE IF NOT EXISTS Tag
(
    tag_id INTEGER NOT NULL PRIMARY KEY,
    value TEXT NOT NULL,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table TagDoku
CREATE TABLE IF NOT EXISTS TagDocu
(
    tag TEXT NOT NULL PRIMARY KEY,
    description TEXT NOT NULL,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table Parameterset
CREATE TABLE IF NOT EXISTS Parameterset
(
    parameterset_name TEXT NOT NULL PRIMARY KEY,
    duplicate TEXT DEFAULT "replace" NOT NULL,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table Parameter
CREATE TABLE IF NOT EXISTS Parameter
(
    parameter_id INTEGER NOT NULL PRIMARY KEY,
    parameter_name TEXT NOT NULL,
    type TEXT DEFAULT "string" NOT NULL,
    export INTEGER DEFAULT 0 NOT NULL,
    unit TEXT DEFAULT "" NOT NULL,
    mode TEXT DEFAULT "text" NOT NULL,
    separator TEXT DEFAULT "," NOT NULL,
    update_mode TEXT DEFAULT "never" NOT NULL,
    duplicate TEXT DEFAULT "none" NOT NULL,
    value TEXT NOT NULL,
    parameterset_name TEXT NOT NULL,
    FOREIGN KEY (parameterset_name) REFERENCES Parameterset(parameterset_name) ON DELETE CASCADE
);

-- Table Fileset
CREATE TABLE IF NOT EXISTS Fileset
(
    fileset_name TEXT NOT NULL PRIMARY KEY,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table File
CREATE TABLE IF NOT EXISTS File
(
    file_id INTEGER NOT NULL PRIMARY KEY,
    type TEXT NOT NULL,
    path TEXT NOT NULL,
    source_dir TEXT DEFAULT "" NOT NULL,
    name TEXT,
    file_path_ref TEXT DEFAULT "" NOT NULL,
    active TEXT DEFAULT "true" NOT NULL,
    is_internal_ref INTEGER DEFAULT 0 NOT NULL,
    target_dir TEXT DEFAULT "" NOT NULL,
    fileset_name TEXT NOT NULL,
    FOREIGN KEY (fileset_name) REFERENCES Fileset(fileset_name) ON DELETE CASCADE
);

-- Table Substituteset
CREATE TABLE IF NOT EXISTS Substituteset
(
    substituteset_name TEXT NOT NULL PRIMARY KEY,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table Substitutefile
CREATE TABLE IF NOT EXISTS Substitutefile
(
    substitutefile_id INTEGER NOT NULL PRIMARY KEY,
    in_file TEXT NOT NULL,
    out_file TEXT NOT NULL,
    out_mode TEXT DEFAULT "w" NOT NULL,
    substituteset_name TEXT NOT NULL,
    FOREIGN KEY (substituteset_name) REFERENCES Substituteset(substituteset_name) ON DELETE CASCADE
);

-- Table Substitute
CREATE TABLE IF NOT EXISTS Substitute
(
    substitute_id INTEGER NOT NULL PRIMARY KEY,
    source TEXT NOT NULL,
    dest TEXT NOT NULL,
    mode TEXT DEFAULT "text" NOT NULL,
    substituteset_name TEXT NOT NULL,
    FOREIGN KEY (substituteset_name) REFERENCES Substituteset(substituteset_name) ON DELETE CASCADE
);

-- Table Step
CREATE TABLE IF NOT EXISTS Step
(
    step_name TEXT NOT NULL PRIMARY KEY,
    iterations INTEGER DEFAULT 1 NOT NULL,
    cycles INTEGER DEFAULT 1 NOT NULL,
    depend TEXT DEFAULT "" NOT NULL,
    export INTEGER DEFAULT 0 NOT NULL,
    active TEXT DEFAULT "true" NOT NULL,
    max_async TEXT DEFAULT "0" NOT NULL,
    work_dir TEXT,
    suffix TEXT DEFAULT "" NOT NULL,
    procs INTEGER DEFAULT 1 NOT NULL,
    shared TEXT,
    do_log_file TEXT DEFAULT "None" NOT NULL,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table Operation
CREATE TABLE IF NOT EXISTS Operation
(
    operation_id INTEGER NOT NULL PRIMARY KEY,
    do TEXT NOT NULL,
    error_filename TEXT,
    async_filename TEXT,
    stdout_filename TEXT DEFAULT "stdout" NOT NULL,
    stderr_filename TEXT DEFAULT "stderr" NOT NULL,
    break_filename TEXT,
    active TEXT DEFAULT "true" NOT NULL,
    shared INTEGER DEFAULT 0 NOT NULL,
    work_dir TEXT,
    step_name TEXT NOT NULL,
    FOREIGN KEY (step_name) REFERENCES Step(step_name) ON DELETE CASCADE
);

-- Table Prepare
CREATE TABLE IF NOT EXISTS Prepare
(
    prepare_id INTEGER NOT NULL PRIMARY KEY,
    do TEXT NOT NULL,
    stdout_filename TEXT DEFAULT "stdout" NOT NULL,
    stderr_filename TEXT DEFAULT "stderr" NOT NULL,
    active TEXT DEFAULT "true" NOT NULL,
    work_dir TEXT,
    fileset_name TEXT NOT NULL,
    FOREIGN KEY (fileset_name) REFERENCES Fileset(fileset_name) ON DELETE CASCADE
);

-- Table UsedParameterset
CREATE TABLE IF NOT EXISTS UsedParameterset
(
    parameterset_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    PRIMARY KEY (parameterset_name, step_name),
    FOREIGN KEY (parameterset_name) REFERENCES Parameterset(parameterset_name) ON DELETE CASCADE,
    FOREIGN KEY (step_name) REFERENCES Step(step_name) ON DELETE CASCADE
);

-- Table UsedFileset
CREATE TABLE IF NOT EXISTS UsedFileset
(
    fileset_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    PRIMARY KEY (fileset_name, step_name),
    FOREIGN KEY (fileset_name) REFERENCES Fileset(fileset_name) ON DELETE CASCADE,
    FOREIGN KEY (step_name) REFERENCES Step(step_name) ON DELETE CASCADE
);

-- Table UsedSubstituteset
CREATE TABLE IF NOT EXISTS UsedSubstituteset
(
    substituteset_name TEXT NOT NULL,
    step_name TEXT NOT NULL,
    PRIMARY KEY (substituteset_name, step_name),
    FOREIGN KEY (substituteset_name) REFERENCES Substituteset(substituteset_name) ON DELETE CASCADE,
    FOREIGN KEY (step_name) REFERENCES Step(step_name) ON DELETE CASCADE
);

-- Table Workpackage
CREATE TABLE IF NOT EXISTS Workpackage
(
    workpackage_id INTEGER NOT NULL PRIMARY KEY,
    iteration INTEGER NOT NULL,
    cycle INTEGER NOT NULL,
    step_name TEXT NOT NULL,
    status TEXT DEFAULT "open" NOT NULL,
    done_time TEXT DEFAULT NULL,
    FOREIGN KEY (step_name) REFERENCES Step(step_name) ON DELETE CASCADE
);

-- Table WorkpackageParents
CREATE TABLE IF NOT EXISTS WorkpackageParents
(
    workpackage_id INTEGER NOT NULL,
    parent_workpackage_id INTEGER NOT NULL,
    PRIMARY KEY (workpackage_id, parent_workpackage_id),
    FOREIGN KEY (workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE,
    FOREIGN KEY (parent_workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE
);

-- Table WorkpackageSibling
CREATE TABLE IF NOT EXISTS WorkpackageSibling
(
    workpackage_id INTEGER NOT NULL,
    sibling_workpackage_id INTEGER NOT NULL,
    PRIMARY KEY (workpackage_id, sibling_workpackage_id),
    FOREIGN KEY (workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE,
    FOREIGN KEY (sibling_workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE
);

-- Table OperationStatus
CREATE TABLE IF NOT EXISTS OperationStatus
(
    workpackage_id INTEGER NOT NULL,
    operation_id INTEGER NOT NULL,
    status TEXT DEFAULT "open" NOT NULL,
    PRIMARY KEY (workpackage_id, operation_id),
    FOREIGN KEY (workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE,
    FOREIGN KEY (operation_id) REFERENCES Operation(operation_id) ON DELETE CASCADE
);

-- Table SelectedParameter
CREATE TABLE IF NOT EXISTS SelectedParameter
(
    parameter_id INTEGER NOT NULL,
    workpackage_id INTEGER NOT NULL,
    selected TEXT NOT NULL,
    idx INTEGER,
    PRIMARY KEY (parameter_id, workpackage_id, idx),
    FOREIGN KEY (parameter_id) REFERENCES Parameter(parameter_id) ON DELETE CASCADE,
    FOREIGN KEY (workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE
);

-- Table Environment
CREATE TABLE IF NOT EXISTS Environment
(
    environment_name TEXT NOT NULL PRIMARY KEY,
    value TEXT,
    env INTEGER NOT NULL
);

-- Table WorkpackageEnvironment
CREATE TABLE IF NOT EXISTS WorkpackageEnvironment
(
    environment_name TEXT NOT NULL,
    workpackage_id INTEGER NOT NULL,
    PRIMARY KEY (environment_name, workpackage_id),
    FOREIGN KEY (environment_name) REFERENCES Environment(environment_name) ON DELETE CASCADE,
    FOREIGN KEY (workpackage_id) REFERENCES Workpackage(workpackage_id) ON DELETE CASCADE
);

-- Table Patternset
CREATE TABLE IF NOT EXISTS Patternset
(
    patternset_name TEXT NOT NULL PRIMARY KEY,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table Pattern
CREATE TABLE IF NOT EXISTS Pattern
(
    pattern_name TEXT NOT NULL PRIMARY KEY,
    type TEXT DEFAULT "string" NOT NULL,
    unit TEXT DEFAULT "" NOT NULL,
    mode TEXT DEFAULT "pattern" NOT NULL,
    dotall INTEGER DEFAULT 0 NOT NULL,
    pattern_default TEXT,
    value TEXT NOT NULL,
    patternset_name TEXT NOT NULL,
    FOREIGN KEY (patternset_name) REFERENCES Patternset(patternset_name) ON DELETE CASCADE
);

-- Table Analyser
CREATE TABLE IF NOT EXISTS Analyser
(
    analyser_name TEXT NOT NULL PRIMARY KEY,
    reduce INTEGER DEFAULT 1 NOT NULL,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table AnalyseFile
CREATE TABLE IF NOT EXISTS AnalyseFile
(
    analysefile_id INTEGER NOT NULL PRIMARY KEY,
    path TEXT NOT NULL,
    analyser_name TEXT NOT NULL,
    FOREIGN KEY (analyser_name) REFERENCES Analyser(analyser_name) ON DELETE CASCADE
);

-- Table AnalyserPattern
CREATE TABLE IF NOT EXISTS AnalyserPattern
(
    patternset_name TEXT NOT NULL,
    analyser_name TEXT NOT NULL,
    PRIMARY KEY (patternset_name, analyser_name),
    FOREIGN KEY (analyser_name) REFERENCES Analyser(analyser_name) ON DELETE CASCADE,
    FOREIGN KEY (patternset_name) REFERENCES Patternset(patternset_name) ON DELETE CASCADE
);

-- Table AnalyseFilePattern
CREATE TABLE IF NOT EXISTS AnalyseFilePattern
(
    patternset_name TEXT NOT NULL,
    analysefile_id INTEGER NOT NULL,
    PRIMARY KEY (patternset_name, analysefile_id),
    FOREIGN KEY (analysefile_id) REFERENCES AnalyseFile(analysefile_id) ON DELETE CASCADE,
    FOREIGN KEY (patternset_name) REFERENCES Patternset(patternset_name) ON DELETE CASCADE
);

-- Table AnalyseStep
CREATE TABLE IF NOT EXISTS AnalyseStep
(
    step_name TEXT NOT NULL,
    analysefile_id INTEGER NOT NULL,
    PRIMARY KEY (step_name, analysefile_id),
    FOREIGN KEY (step_name) REFERENCES Step(step_name) ON DELETE CASCADE,
    FOREIGN KEY (analysefile_id) REFERENCES AnalyseFile(analysefile_id) ON DELETE CASCADE
);

-- Table Result
CREATE TABLE IF NOT EXISTS Result
(
    result_id INTEGER NOT NULL PRIMARY KEY,
    result_dir TEXT,
    benchmark_id INTEGER NOT NULL,
    FOREIGN KEY (benchmark_id) REFERENCES Benchmark(benchmark_id)
);

-- Table ResultAnalyser
CREATE TABLE IF NOT EXISTS ResultAnalyser
(
    result_id INTEGER NOT NULL,
    analyser_name TEXT NOT NULL,
    PRIMARY KEY (result_id, analyser_name),
    FOREIGN KEY (analyser_name) REFERENCES Analyser(analyser_name) ON DELETE CASCADE,
    FOREIGN KEY (result_id) REFERENCES Result(result_id) ON DELETE CASCADE
);

-- Table ResultTable
CREATE TABLE IF NOT EXISTS ResultTable
(
    table_name TEXT NOT NULL PRIMARY KEY,
    style TEXT DEFAULT "csv" NOT NULL,
    separator TEXT DEFAULT "," NOT NULL,
    filter TEXT,
    transpose INTEGER DEFAULT 0 NOT NULL,
    sort TEXT,
    result_id INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES Result(result_id) ON DELETE CASCADE
);

-- Table ResultTableColumn
CREATE TABLE IF NOT EXISTS ResultTableColumn
(
    column_id INTEGER NOT NULL PRIMARY KEY,
    column_name TEXT NOT NULL,
    title TEXT,
    format TEXT,
    colw TEXT,
    table_name TEXT NOT NULL,
    FOREIGN KEY (table_name) REFERENCES ResultTable(table_name) ON DELETE CASCADE
);

-- Table ResultSyslog
CREATE TABLE IF NOT EXISTS ResultSyslog
(
    syslog_name TEXT NOT NULL PRIMARY KEY,
    address TEXT,
    format TEXT,
    filter TEXT,
    host TEXT,
    port INTEGER DEFAULT 541 NOT NULL,
    sort TEXT,
    result_id INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES Result(result_id) ON DELETE CASCADE
);

-- Table ResultSyslogKey
CREATE TABLE IF NOT EXISTS ResultSyslogKey
(
    syslogkey_id INTEGER NOT NULL PRIMARY KEY,
    syslogkey_name TEXT,
    title TEXT,
    format TEXT,
    syslog_name TEXT NOT NULL,
    FOREIGN KEY (syslog_name) REFERENCES ResultSyslog(syslog_name) ON DELETE CASCADE
);

-- Table ResultDatabase
CREATE TABLE IF NOT EXISTS ResultDatabase
(
    database_name TEXT NOT NULL PRIMARY KEY,
    filter TEXT,
    file TEXT,
    result_id INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES Result(result_id) ON DELETE CASCADE
);

-- Table ResultDatabaseKey
CREATE TABLE IF NOT EXISTS ResultDatabaseKey
(
    databasekey_id INTEGER NOT NULL PRIMARY KEY,
    databasekey_name TEXT NOT NULL,
    title TEXT,
    format TEXT,
    is_primary INTEGER DEFAULT 0 NOT NULL,
    database_name TEXT NOT NULL,
    FOREIGN KEY (database_name) REFERENCES ResultDatabase(database_name) ON DELETE CASCADE
);

-- Table ResultFigure
CREATE TABLE IF NOT EXISTS ResultFigure
(
    figure_name TEXT NOT NULL PRIMARY KEY,
    title TEXT,
    savefig TEXT,
    showfig TEXT,
    filter TEXT,
    result_id INTEGER NOT NULL,
    FOREIGN KEY (result_id) REFERENCES Result(result_id) ON DELETE CASCADE
);

-- Table ResultFigurePlot
CREATE TABLE IF NOT EXISTS ResultFigurePlot
(
    plot_id INTEGER NOT NULL PRIMARY KEY,
    legend TEXT,
    xlabel TEXT,
    ylabel TEXT,
    xscale TEXT,
    yscale TEXT,
    figure_name TEXT NOT NULL,
    FOREIGN KEY (figure_name) REFERENCES ResultFigure(figure_name) ON DELETE CASCADE
);

-- Table ResultFigurePlotData
CREATE TABLE IF NOT EXISTS ResultFigurePlotData
(
    data_id INTEGER NOT NULL PRIMARY KEY,
    x TEXT,
    y TEXT,
    groupby TEXT,
    plot_type TEXT,
    label TEXT,
    color TEXT,
    marker TEXT,
    linestyle TEXT,
    plot_id TEXT NOT NULL,
    FOREIGN KEY (plot_id) REFERENCES ResultFigurePlot(plot_id) ON DELETE CASCADE
);
