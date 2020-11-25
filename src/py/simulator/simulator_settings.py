import isodate


class SimulationSettingsConstants:
    ROOT_TAG = 'simulation-settings'
    VERSION_ATTR = 'version'
    RUN_COUNT_ATTR = 'run-count'
    FILES_TAG = 'files'
    ARCHIVE_TAG = 'archive'
    ARCHIVE_PATH_ATTR = 'path'
    ARCHIVE_TYPE_ATTR = 'type'
    SIM_TIMES_TAG = 'simulation-times'
    SIM_START_ATTR = 'simulation-start-time'
    SIM_TIMEZONE_ATTR = 'utc-offset'
    SIM_EVALUATION_LENGTH_ATTR = 'evaluation-length'
    SIM_SEED_LENGTH_ATTR = 'seed-length'
    SIM_TIME_STEPS_ATTR = 'time-steps-per-second'
    SEEDING_TAG = 'seeding'
    SEEDING_FIRST_SEED_ATTR = 'random-seed-first-run'
    SEEDING_SEED_INCREMENT_ATTR = 'random-seed-increment'
