## Queue Discipline

Before to process incoming requests, services store them in a queue. The *queue discipline* governs the order in which 
these requests are taken from the queue. There are two options: either First-In-First-Out (FIFO) and Last-In-First-Out 
(LIFO). Using a FIFO, the next request is the 'oldest' one, that is the first that arrived, as opposed to 
LIFO, where the next request it the 'youngest' one, that is the last one that arrived.
 
Queue discipline appears in the `settings` section, after the keyword `queue`. It can take either value `FIFO` or value 
`LIFO`, as in the following example. By default, services use a FIFO queue.

    service DB {
        settings { queue: LIFO }
            
        operation select {
            think 5
        }
    }

