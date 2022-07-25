import gym
import numpy as np

from abc import ABC


# This class is inherited from the abstract class gym.ActionWrapper that is used to filter out the actions that are not relevant
# for the current environment.
class OvergroundActionShaper(gym.ActionWrapper, ABC):
    def __init__(self, env, vertical_angle=7.5, horizontal_angle=20):
        super().__init__(env)

        # These two lines define the angle of the camera rotation
        self.vertical_angle = vertical_angle
        self.horizontal_angle = horizontal_angle

        # The list of all possible actions the bot can take while being over ground
        self.new_actions = [
            [('attack', 1)],
            [('back', 1)],
            [('left', 1)],
            [('right', 1)],
            [('forward', 1)],
            [('forward', 1), ('jump', 1), ('sprint', 1)],
            [('forward', 1), ('jump', 1)],
            [('camera', [-self.horizontal_angle, 0])],
            [('camera', [self.horizontal_angle, 0])],
            [('camera', [0, self.vertical_angle])],
            [('camera', [0, -self.vertical_angle])],
        ]

        # Gym envs possess a special field – 'action_space'. While 'self.new_actions' is just a list of actions,
        # the action space of environment is an object of gym.spaces.Space (e.g. Dict or Discrete) type, that defines
        # types of actions
        self.new_action_space = []
        for action_pair in self.new_actions:
            # env.action_space.sample() returns a random sample of actions at one time step.
            # env.action_space.noop() returns a sample without active actions.
            act = self.env.action_space.noop()
            for action, value in action_pair:
                act[action] = value
                # 'act' is a sample of action_space where only the required action is active.

            self.new_action_space.append(act)

        self.action_space = gym.spaces.Discrete(len(self.new_action_space))

    # action() is a method that must be overwritten so that step() could work correctly
    def action(self, action):
        return self.new_action_space[action]


# This function gets the gym.spaces.Dict of actions and returns a numpy array of active actions during each step
def normalize_actions(actions, batch_size, vertical_padding=7.5, horizontal_padding=5):
    camera_actions = actions["camera"].squeeze()
    attack_actions = actions["attack"].squeeze()
    forward_actions = actions["forward"].squeeze()
    sprint_actions = actions["sprint"].squeeze()
    back_actions = actions["back"].squeeze()
    left_actions = actions["left"].squeeze()
    right_actions = actions["right"].squeeze()
    jump_actions = actions["jump"].squeeze()

    actions = np.zeros((batch_size,), dtype=np.int)

    for i in range(len(camera_actions)):
        # Moving camera has the highest priority
        if camera_actions[i][0] < -horizontal_padding:
            actions[i] = 7
        elif camera_actions[i][0] > horizontal_padding:
            actions[i] = 8
        elif camera_actions[i][1] > vertical_padding:
            actions[i] = 9
        elif camera_actions[i][1] < -vertical_padding:
            actions[i] = 10

        # Then jump with/without moving forward
        elif jump_actions[i] and forward_actions[i]:
            if sprint_actions[i]:
                actions[i] = 5
            else:
                actions[i] = 6

        # Just move forward if there is no jumping action
        elif forward_actions[i]:
            actions[i] = 4

        # Then other navigation actions
        elif back_actions[i]:
            actions[i] = 1
        elif left_actions[i]:
            actions[i] = 2
        elif right_actions[i]:
            actions[i] = 3

        # Attacking has the lowest priority
        elif attack_actions[i]:
            actions[i] = 0
        else:
            # No reasonable mapping (will be ignored after applying a mask)
            actions[i] = -1

    return actions
