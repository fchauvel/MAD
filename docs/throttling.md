## Throttling
 
Throttling controls whether a service accepts or rejects incoming requests, generally based on the number of
pending requests. This filtering is controled by active queue management algorithms (AQM) such as TailDrop, RED, or 
CoDel The throttling algorithm is configured in the settings as follows:

    service DB:
        settings:
            queue: LIFO
            throttling: tail-drop(50)
            
        operation select:
            think 5

Here, we specify that our DB service throttles incoming requests using the `tail-drop` algorithm. TailDrop simply drops
requests once the queue has reached the specified capacity (here 50 pending requests). By default, throttling is disabled: 
services store requests until they exhaust their internal resources (using `throttling: none`).