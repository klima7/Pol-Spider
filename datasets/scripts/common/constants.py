from pathlib import Path


DATASETS_PATH = Path(__file__).parent.parent.parent

COMPONENTS_PATH = DATASETS_PATH / 'components'
COMPLETE_PATH = DATASETS_PATH / 'complete'

SAMPLES_PATH = COMPONENTS_PATH / 'samples'
DATABASE_PATH = COMPONENTS_PATH / 'database'
BASE_PATH = COMPONENTS_PATH / 'base'
TRANS_PATH = COMPONENTS_PATH / 'schema_trans'
