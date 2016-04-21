## Service Invocations

Services and clients can invoke other services operations either synchronously or asynchronously. The main difference is
that synchronous invocations will paused the task until a response is received. 

### Synchronous Invocations
Synchronous invocations&mdash;or "queries" in MAD&mdash; will wait for a response before to proceed. Note that
MAD assumes non-blocking I/O, so the worker will be released but the execution of the code snippet will only continues
once a reply has been received. See the example below:

    client Browser:
        every 10:
            query DB/Select
            think 5
            
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
