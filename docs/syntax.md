
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
            throttling: TailDrop
            autoscaling: Rule(utilisation)
            
        operation select:
            think 5
            
#### Queue Discipline

Before to process incoming requests, services store them in a queue. The *queue discipline* governs the order in which 
these requests are taken from the queue. There are two options: either First-In-First-Out (FIFO) and Last-In-First-Out 
(LIFO). Using a FIFO, the next request is the 'oldest' one, that is the first that arrived, as opposed to 
LIFO, where the next request it the 'youngest' one, that is the last one that arrived.
 
Queue discipline appears in the `settings` section, after the keyword `queue`. It can take either value `FIFO` or value 
`LIFO`, as in the following example. By default, services use a FIFO queue.

    service DB:
    
        settings:
            queue: LIFO
            
        operation select:
            think 5

#### Autoscaling

Autoscaling controls the number of service instance (or replicas) that are used to processing incoming requests. All 
instances share the same unique queue. Two main parameters govern autoscaling, namely the limits and the policy. The limits
set the minimum and maximum number of replicas, whereas the policy defines how the number of replicas is calculated 
according to the state of the service.

    service DB:
    
        settings:
            autoscaling:
                period: 10
                limits: [1, 20]
                policy: rule-based(utilisation, 70, 80)
        
        operation select:
            think 5
                
In this example, the autoscaling runs every 10 units of time and computes a number of instances between 1 and 20. This 
number results from two rules: 
 * when utilisation raises above 80 %, a new instance is started
 * when utilisation drops below 70 %, a existing instance is stopped
 
#### Throttling
 
Throttling controls whether a service accepts or reject incoming requests, generally based on the length of the queue of
pending requests. This filtering is done by active queue management algorithms such as TailDrop, RED, CoDel, 
etc. The throttling algorithm is configured in the settings as follows:

    service DB:
        settings:
            queue: LIFO
            throttling: TailDrop(50)
            
        operation select:
            think 5

Here, we specify that our DB service throttles incoming requests using the TailDrop algorithm. TailDrop simply drops
requests once the queue reach the specified capacity, here 50 pending requests.