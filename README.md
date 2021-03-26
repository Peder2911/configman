
# Fitin

A very simple small package that makes it easier to write apps that fit in to
various configuration environments.

Installation:
```
 pip install fitin
```
Usage:
```
from fitin import seek_config,environs_resolver,dict_resolver
overrides = {"my":"config"}
config = seek_config([dict_resolver(overrides),environs_resolver()])
config("my") # config
```

