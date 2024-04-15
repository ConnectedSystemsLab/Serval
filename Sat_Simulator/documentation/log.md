Module log
==========
Code to log events to process data.

Functions
---------

    
`Log(description: str, *args) ‑> None`
:   

    
`calculate_latency() ‑> List[float]`
:   Calculates and prints the calculated latency.
    
    Currently handles that any object will create data with Log("Data Created", Data),
    then the data class will create every packet with Log("Packet Created by ", Data , Packet)
    and then the recieve ground station will log with Log("Iot Recieved packet:", Packet)

    
`plot_collisions()`
: