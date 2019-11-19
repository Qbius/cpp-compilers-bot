from cpp_reference import get_cpp_features_map
from discord_bot_interface import command, task, run, create_state, client

@command
def subscribe(message, state):
    state.subs.add(message.author.id)

@command
def unsubscribe(message, state):
    state.subs.remove(message.author.id)

@task.loop(seconds = 60)
def check_cpp_reference(state):
    old_features = state.features
    new_features = get_cpp_features_map()
    for version, new_features_set in new_features.items():
        

    {version: diff for version, new_feature_set in new_features.items() if (diff := (new_feature_set - old_features[version]))}
    return [client.get_user(usr_id).send("hehe") for usr_id in state.subs]

run(default_state = create_state(subs = set(), features = get_cpp_features_map()))