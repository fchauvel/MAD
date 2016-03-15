# MAD &mdash; Microservices Architecture Dynamics

MAD is a domain specific language to simulate microservices architecture. MAD focuses on their dynamics, that is how
various defensive mechanisms get along, including autoscaling rules, throttling policies, back-off protocols, timeout 
and the likes.

The simple possible architecture you can describe, say in the file 'sample.mad' is shown below. It captures a single
services offering an operation 'Select' that takes 10 simulation steps to complete. A client, here called 'Browser', query
this operation every 5 unit of steps.

    service DB:
        operation Select:
            think 10
            
    client Browser:
        every 5:
            query DB/Select

MAD will simulate their behaviour and output traces for both service and clients, including queue length, emission rate, 
utilisation and many other measures.

## Install

	$> pip install mad

## Use

	$> python3 -m mad sample.mad 1000
	
## Doesn't work?

If you  give it a try, please report any bugs, issues, feature request or missing documentation using 
the [issue tracker](https://github.com/fchauvel/mad/issues).
Should you need any further information, feel free to email [me](mailto:franck.chauvel@gmail.com)