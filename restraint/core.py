# A global variable for holding the configuration of django restraint
RESTRAINT_CONFIG = {}


def register_restraint_config(restraint_config):
    RESTRAINT_CONFIG.update(restraint_config)


def get_restraint_config():
    if RESTRAINT_CONFIG:
        return RESTRAINT_CONFIG
    else:
        raise RuntimeError('No restraint config has been registered')
