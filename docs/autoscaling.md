## Autoscaling

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
 