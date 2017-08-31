
'''
These templates are used to craft xml messages to the codec

NOTE: it is very important not to have any whitespace before

Corrrect
e.g message = """<?xml version="1.0"?>

Incorrect
e.g message = """ <?xml version="1.0"?>

'''

survey = """<?xml version="1.0"?>
<Command>
  <UserInterface>
    <Message>
      <Prompt>
        <Display command="True"> 
          <Title>Video Services</Title>
          <Text>Please rate the quaility of your previous call</Text>
          <FeedbackId>1</FeedbackId>
          <Option.1>Excellent</Option.1>
          <Option.2>Good</Option.2>
          <Option.3>Poor</Option.3>
          <Option.4>No Response</Option.4>
        </Display>
      </Prompt>
    </Message>
  </UserInterface>
</Command>
"""

dial = """<?xml version="1.0"?>
<Command>
    <Dial command="True">
        <Number>{}</Number>
    </Dial> 
</Command>
"""

register = """<?xml version="1.0"?>
<Command>
	<HttpFeedback>
		<Register command="True"> 
			<FeedbackSlot>1</FeedbackSlot> 
			<ServerUrl>{}</ServerUrl> 
			<Format>JSON</Format>
			<Expression item="1">/Event/CallDisconnect</Expression>
			<Expression item="2">/Event/UserInterface/Message</Expression>
			<Expression item="3">/Status/Call</Expression>
			<Expression item="4">/Event/UserInterface/Extensions/Widget</Expression>
		</Register>
	</HttpFeedback> 
</Command>
"""

last = """<?xml version="1.0"?>
<Command>
	<CallHistory>
		<Get command="True"> 
			<Filter>All</Filter> 
			<Offset>0</Offset> 
			<Limit>1</Limit>
          	<DetailLevel>Full</DetailLevel>
		</Get>
	</CallHistory> 
</Command>
"""
