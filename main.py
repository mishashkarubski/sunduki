import minerl
import logging
import gym


def main():
    logging.basicConfig(level=logging.DEBUG)
    env = gym.make('MineRLNavigateDense-v0')
    obs = env.reset()
    done = False
    net_reward = 0

    while not done:
        env.render()
        action = env.action_space.noop()

        action['camera'] = [0, 0.03 * obs["compass"]["angle"]]
        action['back'] = 0
        action['forward'] = 1
        action['jump'] = 1
        action['attack'] = 1

        obs, reward, done, info = env.step(action)

        net_reward += reward

        print(obs)


if __name__ == '__main__':
    main()
