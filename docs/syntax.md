
# The MAD Syntax

We detail below how you can describe the services that make your system. 

## Describing your Service

In MAD each service is uniquely identified by its name, a string composed letters, digit or extra characters such as 
'_' for instance. Below is the simplest one we can write: A so called 'DB' service, exposing one operation named 
'select' that takes 5 unit of time to complete.

    service DB:
        operation select:
            think 5

We could add other operations, but we will that this as a starting point.

### Service Configuration

The key feature of MAD is to let you specify various settings that eventually affect the performance of the service or
the system its belongs to. These settings include the queue discipline (FIFO or LIFO), the throttling policy (taildrop, 
RED, BLUE, etc.) the autoscaling policy (rule-based, PID, etc.) the service differentiation policy, etc.  

Settings are parts of the service description. Our database example could be therefore detailed as follows:
 
    service DB:
    
        settings:
            queue: LIFO
            throttling: tail-drop(50)
            autoscaling: Rule(utilisation)
            
        operation select:
            think 5
            