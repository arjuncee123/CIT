from collections import Counter
from qibullet import SimulationManager
import gtts
from playsound import playsound
import threading
import time
from OpenCV import detect_face
import pygame

from rasa import run, model
from rasa_sdk.executor import ActionExecutor
from rasa_sdk.interfaces import Action



class GreetAction(Action):
    def name(self) -> str:
        return "action_greet"
    
    def run(self,dispatcher, tracker, domain) -> list:
        dispatcher.utter_message("Hello, How can I help you?")

class GoodByeAction(Action):
    def name(self) -> str:
        return "action_goodbye"

    def run(self, dispatcher, tracker, domain) -> list:
        dispatcher.utter_message("Goodbye! Have a nice day.")        



class BehaviorRealizer():

    def __init__(self):
        # Loading Robot and  Ground
        simulation_manager = SimulationManager()
        client = simulation_manager.launchSimulation(gui=True)

        self.pepper = simulation_manager.spawnPepper(client, spawn_ground_plane=True)
        self.elbowmovement = -3.0

    def realize_gaze(self, gesture):
        self.pepper.setAngles(["HeadYaw", "HeadPitch"], [0.0, -0.3], 1.0)
        print(f"Head gesture '{gesture}' realized.")

    def realize_speech(self, text):
        # Convert the text to speech using GTTS.
        tts = gtts.gTTS(text, lang="en")
        tts.save(text+'.mp3')
        # Play the speech audio using playsound.


        pygame.mixer.init()
        pygame.mixer.music.load(text+".mp3")
        pygame.mixer.music.play()

        #playsound(text+'.mp3')
        print(f"Speech '{text}' realized.")

    def realize_gesture(self):
        # Raise the right hand from the user's point of view.
        self.pepper.setAngles(
            ["LShoulderPitch", "LElbowRoll", "LElbowYaw", "LWristYaw"],
            [0.0, -45, -1.5, 45],
            1.0,
        )
        print("Right hand raised.")

        # Wait for 1 second.
        time.sleep(1.0)

        # Wave the right hand.
        for i in range(5):
            # Move the elbow joint back and forth.
            self.pepper.setAngles(["LElbowYaw"], [4.0], 1.0)
            self.pepper.setAngles(["LElbowYaw"], [-4.0], 1.0)
        print("Hand waving.")

        # Wait for 1 second.
        time.sleep(1.0)

        # Lower the right hand.
        self.pepper.setAngles(["LElbowYaw"], [-1.5], 1.0)

    def realize_behavior(self, dictionary):
        print("Realizing behavior...")

        gaze_thread = threading.Thread(target=self.realize_gaze, args=(dictionary["gaze"]["gesture"],))
        speech_thread = threading.Thread(target=self.realize_speech, args=(dictionary["speech"]["text"][0],))
        gesture_thread = threading.Thread(target=self.realize_gesture)

        gaze_thread.start()
        speech_thread.start()
        gesture_thread.start()

        gaze_thread.join()
        speech_thread.join()
        gesture_thread.join()

        # After waving hand is completed, say "Glad to see you."
        self.realize_speech(dictionary["speech"]["text"][1])

    def behavior_realizer(self, dictionary):
        print("behavior_realizer function")
        # Continue with the rest of the multimodal behavior
        behavior_thread = threading.Thread(target=self.realize_behavior, args=(dictionary,))
        behavior_thread.start()
        behavior_thread.join()
        # Reset the agent after the execution
        self.reset_agent()

    def reset_agent(self):
        # To reset the agent to the default state after the execution
        self.pepper.setAngles(['HeadYaw', 'HeadPitch'], [0.0, 0.0], 1.0)
        self.pepper.setAngles(['LShoulderPitch', 'RShoulderPitch', 'RElbowYaw', 'LElbowYaw', 'LElbowRoll', 'LWristYaw'],
                               [0.0, 0.0, 0.0, 0.0, 0.0, 0.0], 1.0)

if __name__ == "__main__":

    # INPUT_OPTIONS = ["done", "show"]  # We have two input options defined currently; done will close the robot simulation and input show will run the simulation

    # user_input = input("Please enter the INPUT :\n1. Show -> To run an application and have a conversation with Pepper Robot\n2. Done -> To exit from the application")


    model_path = "RasaHCI/models"
    trained_model = model.get_local_model(model_path)

    # Start the Rasa action server
    action_executor = ActionExecutor()
    action_executor.register_action(GreetAction())
    action_executor.register_action(GoodByeAction())



    isFaceDetected = detect_face()
    if isFaceDetected:
        behavior = {
        "gesture": {"gesture": "waveHand"},
        "gaze": {"gesture": "nod"},
        "speech": {
            "text": ["Hello", "Glad to see you"]
        }}

        behavior_realizer_class = BehaviorRealizer()  # To create the instance of BehaviorRealizer class
        behavior_realizer_class.behavior_realizer(dictionary=behavior)  # To call behavior_realizer to handle the multimodal behavior    
        run(model=model_path, endpoints='RasaHCI/endpoints.yml')
    else:
        print("Face is not detected. The application starts when a face is detected.")        

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass      

    # repeat_ = True
    # while repeat_:
    #     user_input = input("INPUT : ")  # fetching the input from the user

    #     if str(user_input) == INPUT_OPTIONS[0]:  # if user input's done, then repeat_ flag is set to false which makes the program end
    #         repeat_ = False

    #     elif str(user_input) == INPUT_OPTIONS[1]:  # if user input is "show", it will create an instance of BehaviorRealizer class and perform the functionalities

    #         isFaceDetected = detect_face()
    #         if isFaceDetected:
    #             behavior = {
    #             "gesture": {"gesture": "waveHand"},
    #             "gaze": {"gesture": "nod"},
    #             "speech": {
    #                 "text": ["Hello", "Glad to see you"]
    #             }}

    #             behavior_realizer_class = BehaviorRealizer()  # To create the instance of BehaviorRealizer class
    #             behavior_realizer_class.behavior_realizer(dictionary=behavior)  # To call behavior_realizer to handle the multimodal behavior
    #         else:
    #             print("Face is not detected to start the greetings")


    #     elif not user_input in INPUT_OPTIONS:  # If the user accidentally inputs any other word other than done and show, it will print "Please try again"
    #         print("Please try again: ")  # and the user can provide the input again


#from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple, OrderedDict
