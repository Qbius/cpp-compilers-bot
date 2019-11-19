import pickle
import os

def load_state():
    return type('', (), pickle.load(open('state.info', 'rb')))

def save_state(obj):
    pickle.dump(obj.__dict__, open('state.info', 'wb'))

def __check_if_last_arguments(fun, args):
    fun_params = list(signature(fun).parameters)
    kwarg_params = [k for k in fun_params if k in ['message', 'state']]
    return set(kwarg_params) - set(fun_params[-len(kwarg_params):])
    
import discord
import asyncio
from inspect import signature

client = discord.Client()
print('Initializing...')

available_commands = dict()
class command(object):

    @staticmethod
    def __add_command(prefix, fun):
        not_last_special_args = __check_if_last_arguments(fun, ['message, state'])
        if len(not_last_special_args) > 0:
            raise Error(f"Error while trying to add the {fun.__name__} command: {', '.join(not_last_special_args)} not at the back of the argument list")
        else:
            available_commands[f'{prefix}{fun.__name__}'] = fun
            print(f"Added command {fun.__name__}")

    def __init__(self, fun):
        __add_command('!', fun)

    @staticmethod
    def override_prefix(pref):
        return lambda fun: __add_command(pref, fun)

    @staticmethod
    def __call_command(msg):
        cmd_name, *args = msg.content.split(' ')
        if cmd_name not in available_commands: return
        cmd = available_commands[cmd_name]
        fun_params = signature(cmd).parameters
        kwargs = {k: v for k, v in {'message': msg, 'state': load('state')}.items() if k in fun_params}

        normal_args = [k for k in fun_params.keys() if k not in all_kwargs.keys()]
        if len(normal_args) != len(args):
            args_err_msg = f"Error, expected {len(normal_args)} arguments (got {len(args)})\nExpected arguments: "
            args_err_msg += ','.join([f'{arg_name}' + (f' (default: {fun_params.get(arg_name).default})' if fun_params.get(arg_name).default != Parameter.empty else '') for arg_name in normal_args])
            return args_err_msg
        else:
            return cmd(*args, **kwargs)

@client.event
def on_message(msg):
    command.__call_command(msg)

def event(fun):
    if __check_if_last_arguments(fun, ['state']):
        raise Error("state needs to be the last argument")

    def inner(*a, **kw):
        kwargs = {k: v for k, v in {'state': load_state()}.items() if k in signature(fun).parameters}
        result = fun(*a, **{**kw, **kwargs})
        if 'state' in kwargs.keys(): save_state(kwargs['state'])
        return result

    return client.event(inner)

class task(object):
    @staticmethod
    def __add_task(fun):
        client.loop.create_task(fun)
        print(f"Added task {fun.__name__}")

    def __init__(self, fun):
        __add_task(fun)

    @staticmethod
    def loop(seconds):
        def decorate_loop(fun):
            if __check_if_last_arguments(fun, ['state']):
                raise Error("state needs to be the last argument")

            inner = fun
            if 'state' in signature(fun).parameters:
                def state_inner():
                    state = load_state()
                    fun(state)
                    save_state(state)
                inner = state_inner

            async def loop_task():
                await client.wait_until_ready()
                while not client.is_closed():
                    inner()
                    await asyncio.sleep(seconds)
            
            _add_task(loop_task)

def run(token = open('bot_token').read().strip(), default_state = type('', (), {})()):
    if not os.path.exists('state.info'): save_state(default_state)
    client.run(token)