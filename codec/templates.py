
'''
These templates are used to craft xml messages to the codec

NOTE: it is very important not to have any whitespace before

Corrrect
e.g message = """<?xml version="1.0"?>

Incorrect
e.g message = """ <?xml version="1.0"?>

'''
message = """<?xml version="1.0"?>
<Command>
  <UserInterface>
    <Message>
      <Prompt>
        <Display command="True"> 
          <Title>Video Services</Title>
          <Text>{}</Text>
          <FeedbackId>2</FeedbackId>
          <Option.1>Acknowledge</Option.1>
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

# Template for collecting call history.
# xcommand CallHistory Recents DetailLevel: Full Limit:
last = """<?xml version="1.0"?>
<Command>
    <CallHistory>
        <Recents command="True">
            <DetailLevel>"Full"</DetailLevel>
            <Limit>{}</Limit>
        </Recents>
    </CallHistory> 
</Command>
"""
