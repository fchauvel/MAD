## Service Differentiation
 
Under **service differentiation**, a service varies according to the client identity, the operation or the context. In 
MAD, Each invocation may specify a priority level (as an integer value), which governs the order in which the service will process 
requests. By default, the priority level is 1. 


    service DB {            
        operation Select { think 5 }
    }
            
    client Browser_A {
        every 5 {
            query DB/Select {priority: 10}
        }
    }
            
    client Browser_B {
        every 5 {
            query DB/Select {priority: 5}
        }
    }
    

In this example, we define two clients that query the same operation `DB/Select` but with different priorities. The first one,  
called `Browser_A` gives its requests a priority of 10, as opposed to the second one, which only sets a priority 
of 5. As a result, the `DB`service will never process any request from `Browser_B`, because it will always pick-up 
requests from `Browser_A` first. Note that `Browser_B`s requests are yet accepted and enqueued, but they are never selected for
processing.
