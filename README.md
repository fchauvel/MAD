# MAD &mdash; Microservices Architectures Dynamics

[![shields.io](https://img.shields.io/pypi/v/MAD.svg)](https://pypi.python.org/pypi/MAD)
[![shields.io](https://img.shields.io/pypi/l/MAD.svg)](http://www.gnu.org/licenses/gpl-3.0.en.html)
[![codeship.io](https://img.shields.io/codeship/68381610-6386-0133-dbbe-16f6a7024b95.svg)](https://codeship.com/projects/112817)
[![codecov.io](https://img.shields.io/codecov/c/github/fchauvel/MAD/master.svg)](https://codecov.io/github/fchauvel/MAD)
[![PyPI](https://img.shields.io/pypi/dm/MAD.svg)](http://pypi-ranking.info/module/MAD)



MAD is a discrete event simulator to study the dynamics of microservices architectures where each service encompasses 
several defensive mechanisms, such as timeout, autoscaling, throttling, back-off protocols, etc.

See the [official documentation](http://www.pythonhosted.org/MAD).

## TODO

 * Features
    * Services
        * Support for request differentiation
        * Support for timeout
        * Support for backing-off protocols
        * Monitoring
            * response time
            * incoming request count
            * current timeout
            * current back-off delay per 'partner'
            * incoming/outgoing rejection rate/count
    * Clients
        * Multiple clients
        * Workload patterns
 * Examples
    * SensApp example
 * Tests
    * Test shutting down workers, they shall first complete there current task
    * Test that rejection count is not cumulative
    * Test that the simulation call back the display
 * Refactorings
    * Extract monitoring into a separate simulated entity, which can be configured throughout the settings
    * Format of the logs should be defined by the service itself, not by the factory
    * A test factory shared among simulation test


    
    