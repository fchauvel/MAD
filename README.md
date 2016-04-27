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
    * UI
        * Should place a copy of the simulated file in the output folder
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
            * Delay before workers gets active
        * Actions
            * Probabilistic switch statement, a la 'choice'
    * Clients
        * Multiple clients
        * Workload patterns
 * Bug fixes
    * R Script ylim which are based on the first series, instead of the max of all series
    * timeout activation that fails because the request was not properly paused
    * recursion that exceeds the maximum depth
 * Examples
    * SensApp example
 * Tests
    * Test shutting down workers, they shall first complete there current task
    * Test that rejection count is not cumulative
    * Test that the simulation call back the display
    * Test for retry in an action list in the parser
    * Test timeouts that are activated after the call to send request (what happen if the request is assign to a worker
    right away?)
 * Refactorings
    * A test factory shared among simulation test
    * Move the creation of workers from Service to the autoscaling strategy
    * Split acceptance tests into several files (commons, nominals, errors)
    * Merge test_evaluation and test_interpreter
 
## NEXT RELEASE CHANGE LOG

 * Bug Fixes:
    * Fix in the calculation of the throughput and reliability that leaded to negative values
    * Fix the worker behaviour when request have timeout. They now check whether the task is still pending before to proceed
    * Fiz the invoke and query which now wait for acceptance by the server.
    * Fix the behaviour of the invocation, which take 1 unit of time to send the requests
    * Fix autoscalling issues that exceeds its limits by one.




    