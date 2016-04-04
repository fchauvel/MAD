# MAD &mdash; Microservices Architectures Dynamics

[![shields.io](https://img.shields.io/pypi/v/MAD.svg)](https://img.shields.io/pypi/v/MAD.svg[])
[![shields.io](https://img.shields.io/pypi/l/MAD.svg)](https://img.shields.io/pypi/l/MAD.svg[])
[![codeship.io](https://img.shields.io/codeship/68381610-6386-0133-dbbe-16f6a7024b95.svg)](https://img.shields.io/codeship/68381610-6386-0133-dbbe-16f6a7024b95.svg)
[![codecov.io](https://img.shields.io/codecov/c/github/fchauvel/MAD/master.svg)](https://img.shields.io/codecov/c/github/fchauvel/MAD/master.svg)

MAD is a discrete event simulator to study the dynamics of microservices architectures where each service encompasses 
several defensive mechanisms, such as timeout, autoscaling, throttling, back-off protocols, etc.

See the [official documentation](http://www.pythonhosted.org/MAD).

## TODO

 * Features
    * Services
        * Support for request differentiation
        * Support for timeout
        * Support for throttling policies
        * Monitoring
            * Current timeout
            * Current back-off
            * incoming/outgoing rejection rate/count
    * Clients
        * Multiple clients
        * Workload patterns
 * Improve error reporting
    * Errors in the parameters passed to the CLI
    * Semantic and syntactic errors in MAD files
 * Examples
    * SensApp example
 * Tests
    * Test shutting down workers, they shall first complete there current task
 * Refactorings
    * Extract monitoring into a separate simulated entity, which can be configured throughout the settings
    * Breakdown AST into multiple files
    


    
    