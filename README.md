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
            * response time
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
    * Several folders are created when the simulation takes some much time
    
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

 * Support of an 'ignore-error' primitive
 * Bug Fixes
    * Fix R script to render 'missing values' (i.e., "NA") properly



    