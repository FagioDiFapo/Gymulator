import argparse

def get_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", help="Execution mode between train or test", required=True, type=string, choices=["train","test"])
    parser.add_argument("model_name", help="Name of the model you want to train/test", default="ppo-RocketLander", type=string)

class Trainer:

    MODEL = None

    def __init__(self, model_name):
        self.model_name = model_name

    def train(self, timesteps, nenvs):
        envs = make_vec_env(RocketLander, n_envs=nenvs)
        self.MODEL = PPO(
            policy = 'MlpPolicy',
            env = envs,
            n_steps = 1024,
            batch_size = 64,
            n_epochs = 4,
            gamma = 0.999,
            gae_lambda = 0.98,
            ent_coef = 0.05,
            verbose=1,
            device="cuda")
        self.MODEL.learn(total_timesteps=timesteps)
        self.MODEL.save(self.model_name)

    def test(self):
        eval_env = Monitor(RocketLander(render_mode = "human"))
        if self.MODEL = None: self.MODEL = PPO.load(self.model_name+".zip")

        mean_reward, std_reward = evaluate_policy(model, eval_env, n_eval_episodes=10, deterministic=True)
        print(f"mean_reward={mean_reward:.2f} +/- {std_reward}")


if __name__ == '__main__':
    args = get_arguments()
    trainer = Trainer(args.model_name)

    if args.mode == "train":
        trainer.train(1000000, 16)
    elif args.mode == "test":
        trainer.test()