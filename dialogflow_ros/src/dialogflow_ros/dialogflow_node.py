#!/usr/bin/env python
import rospy
import actionlib
import apiai
import json

from dialogflow_msgs.msg import TextRequestAction, TextRequestResult

# Authentication
SESSION_ID = ''


def _response_to_semantics(response):
    action = response['result']['action']
    parameters = response['result']['parameters']
    semantics = parameters
    semantics['action'] = action
    return semantics


def _response_to_speech(response):
    text_response = response['result']['fulfillment']['speech']
    return text_response


class DialogflowNode(object):
    """
    ROS node for the Dialogflow natural language understanding.

    Dialogflow (previously API.ai) parses natural language into a json string containing the semantics of the text. This
    nose wraps that into a ROS actionlib interface.
    """
    def __init__(self):
        rospy.init_node('dialogflow_node')

        try:
            self._client_access_token = rospy.get_param("~client_access_token")
        except rospy.ROSException:
            rospy.logfatal("Missing required ROS parameter client_access_token")
            exit(1)

        self._server = actionlib.SimpleActionServer('dialogflow', TextRequestAction, self._text_callback, False)
        self._server.start()

        self.ai = apiai.ApiAI(self._client_access_token)

    def _text_callback(self, goal):
        request = self.ai.text_request()
        request.query = goal.text

        rospy.logdebug("Waiting for response...")
        response_html = request.getresponse()

        # Create a dict out of the response
        response_str = response_html.read()
        response = json.loads(response_str)

        rospy.logdebug("Got response:\n%s\nReturning it as action result." % response_str)

        result = TextRequestResult()
        result.semantics = json.dumps(_response_to_semantics(response))
        result.response = _response_to_speech(response)

        self._server.set_succeeded(result)

if __name__ == "__main__":
    dialogflow_node = DialogflowNode()
    rospy.spin()
