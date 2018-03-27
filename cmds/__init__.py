import pkgutil

COMMANDS = {}
__all__ = []

# Dynamically load all submodules in package
for loader, module_name, is_pkg in pkgutil.walk_packages(__path__):
    __all__.append(module_name)
    module = loader.find_module(module_name).load_module(module_name)    
    exec('%s = module' % module_name)

    COMMANDS[module_name] = module.command
