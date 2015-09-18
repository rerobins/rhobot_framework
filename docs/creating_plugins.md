# Creating Component Plugins for Rho Framework

The framework is built upon creating plugins for execution inside the SleekXMPP architecture.  These plugins can generate content, execute commands, or provide additional functionality that can be used by other plugins in the system.  Note: Commands can be implemented as plugins, but due to some idiosyncracies of the SleekXMPP framework, there is an abstract class that provides similar fuctionality for commands.

## SleekXMPP Framework

SleekXMPP requires that all plugins inherit from `sleekxmpp.plugins.base.base_plugin`.  This provides the expected functionality for all plugins.  This means that all plugins must have the following class variables.

* name - the means of looking up the plugin in the architecture.
* description - human readable string that will be used in debug statements
* dependencies - set of dependencies that are required for the plugin to initialize.

## Installing Framework

The documentation of SleekXMPP states that the plugins should be installed using:

```python
bot.register_plugin('plugin_name', module='module_name')
```

This will load the plugin and enable the plugin in a single step.

A better way, that allows for automatic dependency resolution is to break up the load and enable into multiple steps.  If this is not done, you're required to register the plugins in dependency order instead of letting SleekXMPP handle this for you, (which it has unit tests for).

This is done by:

```python
from my_plugins_module import my_plugin
from sleekxmpp.plugins.base import register_plugin

def load_components():
    register_plugin(my_plugin)

########### Then in the bot definition

load_components()

bot = RhoBot()
bot.register_plugin('my_plugin')
```

This will force all of the plugins that my_plugin depends on (and have been registered with the system) will be loaded and enabled before my_plugin is initialized.
