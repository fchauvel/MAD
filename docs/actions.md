## Actions and Service Invocations

Services and clients can perform simple actions, including invoking other services. Services and clients can invoke 
other services operations either synchronously or asynchronously. The main difference is that synchronous invocations 
will paused the task until a response is received. 

### Synchronous Invocations
Synchronous invocations&mdash;or "queries" in MAD&mdash; will wait for a response before to proceed. Note that
MAD assumes non-blocking I/O, so the worker will be released but the execution of the code snippet will only continues
once a reply has been received. See the example below:

    client Browser {
        every 10 {
            query DB/Select
            think 5
        }
    }
            
In this example, we define a client that synchronously invokes the operation `DB/Select` and then thinks for 5 simulation
steps. In this case, the Browser will starts thinking only once it has received a reply (possibly an error) from the `DB`
service. If the invocation had been asynchronous, the Browser would have started to "think" as soon as it would have emitted
the request to the `DB/Select` operation.

#### Timeouts

In practice, we do not want to wait forever for the response and we consider that a request has failed once we waited 
for a given time. The request has **timed out**. MAD lets you specify timeouts on (synchronous invocations only) as shown
in the following example, where we limit the waiting time to 10 simulation steps.

    client Browser {
        every 5 {
            query DB/Select {timeout: 10}
            think 5
        }
    }


### Asynchronous Invocations
Asynchronous invocations do not pause the caller, as opposed to synchronous ones (see above). They represent signals or 
messages where no response is expected. The caller therefore send the message and proceeds with the remaining actions.

    client Browser {
        every 10 {
            invoke DB/Select
            think 5
        }
    }

In this example for instance, every 10 simulation steps, the `Browser` sends a request to the `DB/Select` operations and 
immediately starts thinking for 5 simulation steps, without waiting for any response.

### Retry
Invocations be they synchronous or asynchronous may fail. By default, such a failure will abort the current task and 
propagates to the caller if this happens during the execution of an operation. It is possible however to 'wait and retry'
using alternative back-off policies.

    client Browser {
        every 10 {
            retry(limit=10) {
               query DB/Select
            }
        }
    }

In this example, the Browser will try to query to 'Select' operation of the 'DB' service, retry 10 if necessary. If all these
ten attempts fails, the Browser will record a failure. By default, the Browser waits a constant time (10 simulation steps)
before to retry, but we may also specify back-off policies (exponential of fibonnacci) as follows:

    client Browser {
        every 10 {
            retry(limit=10, delay:exponential(5)) {
               query DB/Select
            }
        }
    }
Here, we specify an [exponential backoff](https://en.wikipedia.org/wiki/Exponential_backoff) policy. The browser will first
wait for 5 minutes and then increases the waiting time exponentially. 


### Thinking
Thinking is a blocking "No-op" operation. It emulate compute-intensive internal tasks. It accepts a fixed duration during
which the underlying worker will be blocked. 

    service DB {
        operation Select {
            think 55
        }
    }
  
 This example specifies that the `select` operation will take 55 simulation steps.
 
### Failing
 
Service may also fail, either systematically or with a given probability.
    
    service DB {
        operation Select {
            fail 0.25
        }
    }
This example specifies that the `select` operation may fail with 0.25 probability.
