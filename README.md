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
        * Monitoring
            * Client status (not only service)
            * Per operation
                * emission rate
            * current timeout
            * current back-off delay per 'partner'
            * incoming/outgoing rejection rate/count
        * Priority / Service differentiation
            * An algorithm that ensures fairness
        * Autoscaling
            * Delay before workers gets active,
            * Expose the metrics in use
        * Actions
            * Probabilistic switch statement, a la 'choice'
    * Clients
        * Multiple clients
        * Workload patterns
 * Bug fixes
 * Examples
    * SensApp example
    * Grafterizer example
    * Example for The Architecture Conference .NET microservice
 * Tests
    * Test shutting down workers, they shall first complete there current task
    * Test that the simulation call back the display
    * Test for retry in an action list in the parser
    * Test timeouts that are activated after the call to send request (what happen if the request is assign to a worker
    right away?)
 * Refactorings
    * A test factory shared among simulation test
    * Move the creation of workers from Service to the autoscaling strategy
    * Merge test_evaluation and test_interpreter
    * Merge throttling and Task pool into Bounded task pool
    * Autoscaling should read statistics from the monitor
    * Monitor should also account for worker counts
 * Quid of Caching
    * Message-Queue/PubSub as a concept?

 
## NEXT RELEASE CHANGE LOG

 * Features
    * Copy the model into the output directory
 * Bug Fixes
    * Fix worker that are not released when the triggering request as been
    discarded and that the emitted request succeed
    * Fix rejection that did not fail the 'parent' request
 * Refactorings
    * Split acceptance tests into several files (commons, nominals, errors)
 


    