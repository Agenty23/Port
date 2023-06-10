# Brief description of FIPA ACL messages

It is a message structure specification which we will be using in this project (implemented in SPADE). It consists of a set of message parameters.

## Message parameters:

- **performative** - the type of the message (only required param)
- **sender** - the sender of the message
- **receiver** - the receiver of the message
- **reply-to** - the address to which the receiver should reply
- **topic** - the topic of the message for specific reaction context (filtering messages with the same performative) (non-standard, implemented for purpose of this project)
- **content** - the content of the message
- **language** - the language in which the content is written
- **encoding** - the encoding of the content (not used in this project)
- **ontology** - the ontology to which the content refers (not used in this project)
- **protocol** - the protocol to be used (not used in this project)
- **conversation-id** - the conversation to which the message refers (not used in this project since SPADE has thread property instead)
- **reply-with** - the identifier of the message
- **in-reply-to** - the identifier of the message to which this message is a reply
- **reply-by** - the date by which the reply is expected

## Performative types:

- **ACCEPT-PROPOSAL** - accept a previously made proposal to perform an action 
- **AGREE** - agree to perform an action
- **CANCEL** - inform receiver that sender has no longer interest in performing an action (by receiver)
- **CFP (CALL-FOR-PROPORSAL)** - call for proposal to perform an action
- **CONFIRM** - confirm that the given preposition is true
- **DISCONFIRM** - confirm that the given preposition is false
- **FAILURE** - inform that the given was attempted but failed
- **INFORM** - inform about some preposition
- **INFORM-IF** - as above, but in boolean form
- **INFORM-REF** - as above, but in reference form
- **NOT-UNDERSTOOD** - inform that the given message was not understood (e.g. handling not implemented)
- **PROPAGATE** - ask for message forwarding
- **PROPOSE** - propose to perform an action (response with **ACCEPT-PROPOSAL** or **REJECT-PROPOSAL**)
- **PROXY** - similar to propagate, but with some additional constrain (e.g. max number of agents to be forwarded)
- **QUERY-IF** - ask if the given preposition is true (response with **INFORM** or **INFOM-IF**)
- **QUERY-REF** - ask for reference to the given preposition (response with **INFORM** or **INFOM-REF**)
- **REFUSE** - refuse to perform an action
- **REJECT-PROPOSAL** - reject a previously made proposal to perform an action
- **REQUEST** - request to perform an action (response with **AGREE** or **REFUSE**)
- **REQUEST-WHEN** - as above, but with additional constrain (e.g. time)
- **REQUEST-WHENEVER** - as above, but with additional constrain (e.g. time) that should be repeated each time the constrain is met