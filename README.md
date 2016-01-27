# MAD &mdash; Microservices Architectures Dynamics

[![shields.io](https://img.shields.io/badge/license-GPLv3+-blue.svg)](https://img.shields.io/badge/license-GPLv3+-blue.svg)
[![codeship.io](https://img.shields.io/codeship/68381610-6386-0133-dbbe-16f6a7024b95.svg)](https://img.shields.io/codeship/68381610-6386-0133-dbbe-16f6a7024b95.svg)
[![codecov.io](https://img.shields.io/codecov/c/github/fchauvel/MAD/master.svg)](https://img.shields.io/codecov/c/github/fchauvel/MAD/master.svg)

MAD is a discrete event simulator to study the dynamics of microservices architectures where each service encompasses 
several interacting feedback loops.

More to come soon.

## TODO

 * Introduce delays before a server is active.
 * Introduce asynchrony between services (request vs. notify)
 * Make samples of DSL.
 
 
An example of DSL

architecture SensApp:

    service Converter:

        configuration:
            scale: per-request         
            queue: None

        operation convert:
            do "conversion" [duration: 15 s]
            trigger Dispatcher::Dispatch 
            
            
    service Dispatcher:
    
        configuration:
            queue: None
                
        operation Dispatch:
            request Registry::check_sensor [on-error: retry; delay: constant(10 s.) ]
            trigger Notifier::notify
            trigger Storage::store_data 
            
            
    service Registry:
       
       operation Check_Sensor:
            do "check" [duration: 15 s]
    
    
    service Storage:
        
        operation store_data:
            request Database::insert


    service Notifier:
        
        operation notify:
            trigger 


environment Test_spike:

    ClientStub Sensors:
        trigger Converter::convert [
            frequency = step (from=0.5 req/s ; to=25 req/s; t=500)
            size = step (from = 100 KB ; to = 25 MB; t = 500)    
         ];
        
    ServerStub Database:
        operation store_data [duration = 1 ms, rejection rate = 0)

````


    
