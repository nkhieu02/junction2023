from huggingface_hub import InferenceClient, AsyncInferenceClient
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional, List, Dict, Any, Callable
from openai import OpenAI
from openai import AsyncOpenAI
from dotenv import load_dotenv
load_dotenv()
import os
import json

@dataclass
class BaseModel(ABC):
    model: str
    api_token: str = None

    @abstractmethod
    def generate(self, input):
        pass

    @abstractmethod
    def agenerate(self, input):
        pass

@dataclass
class Huggingface_Model(BaseModel):
    
    timmeout: Optional[float] = None
    
    def __post_init__(self):
        self.api_token = os.getenv('HUGGINGFACEHUB_API_TOKEN')
        self._client, self._aclient = self.create_client()

    def create_client(self):
        return InferenceClient(model=self.model,
                               token=self.api_token,
                               timeout=self.timmeout),\
               AsyncInferenceClient(model=self.model,
                                    token=self.api_token,
                                    timeout=self.timmeout)
    
    def generate(self, input: str, **kwargs):
        '''
        input (str) — Input text.

        **kwargs:

        details: (bool, optional) — details=True if you want a detailed output (tokens, probabilities, seed, finish reason, etc.). Only available for models running on with the text-generation-inference backend.
        stream (bool, optional) — By default, text_generation returns the full generated text. Pass stream=True if you want a stream of tokens to be returned. Only available for models running on with the text-generation-inference backend.
        model: (str, optional) — The model to use for inference. Can be a model ID hosted on the Hugging Face Hub or a URL to a deployed Inference Endpoint. This parameter overrides the model defined at the instance level. Defaults to None.
        do_sample: (bool) — Activate logits sampling
        max_new_tokens: (int) — Maximum number of generated tokens
        best_of: (int) — Generate best_of sequences and return the one if the highest token logprobs
        repetition_penalty: (float) — The parameter for repetition penalty. 1.0 means no penalty. See this paper for more details.
        return_full_text: (bool) — Whether to prepend the prompt to the generated text
        seed: (int) — Random sampling seed
        stop_sequences: (List[str]) — Stop generating tokens if a member of stop_sequences is generated
        temperature: (float) — The value used to module the logits distribution.
        top_k: (int) — The number of highest probability vocabulary tokens to keep for top-k-filtering.
        top_p: (float) — If set to < 1, only the smallest set of most probable tokens with probabilities that add up to top_p or higher are kept for generation.
        truncate: (int) — Truncate inputs tokens to the given size
        typical_p: (float) — Typical Decoding mass See Typical Decoding for Natural Language Generation for more information
        watermark: (bool) — Watermarking with A Watermark for Large Language Models
        decoder_input_details: (bool) — Return the decoder input token logprobs and ids. You must set details=True as well for it to be taken into account. Defaults to False.
        Outputs:
        - Access text: output.generated_text
        '''
        return self._client.text_generation(input, **kwargs)

    
    async def agenerate(self, input: str, **kwargs):
        '''
        Similar to def generate
        '''
        output = await self._aclient.text_generation(input,**kwargs)
        return output
        
@dataclass
class ChatOpenAI(BaseModel):

    timeout: Optional[float] = None
    
    def __post_init__(self):
        self.api_token = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key = self.api_token)

    def generate(self, input, **kwargs):   
        completion = self.client.chat.completions.create(
        model=self.model,
        messages=input,
        stream=kwargs['stream'],
        )
        return completion
    
    def agenerate(self, input):
        return super().agenerate(input)
    
    def function_calling(self, input: List[dict], tools: Dict[str, Callable], 
                         tool_schemas: List[Dict]) -> List[Dict]:
        
        
        '''
        Input here is basically messages
        Models suitable for this:
        gpt-4
        gpt-4-1106-preview
        gpt-4-0613
        gpt-3.5-turbo
        gpt-3.5-turbo-1106
        gpt-3.5-turbo-0613
        In addition, parallel function calls is supported on the following models:        
        gpt-4-1106-preview
        gpt-3.5-turbo-1106
        
        Output:

        - A list dictionry with 2 keys: name and content, 
        name of the function called and content is response. 
        '''
        messages = input
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tool_schemas,
            tool_choice="auto"
        )
        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls
        # Initiate holde for the responses:
        function_responses = []
        # Check if the model want to call a function:
        if tool_calls:
            for tool_call in tool_calls:
                function_name = tool_call.function.name
                print(function_name)
                if not function_name in tools:
                    print(f'{function_name} is invalid.')
                    continue
                function_to_call = tools[function_name]
                print(function_to_call)
                print(tool_call)
                function_args = json.loads(tool_call.function.arguments)
                input_param = function_args.get("input")
                print(input_param)
                if function_name == 'news_search':
                    function_response = function_to_call(
                        input=input_param,
                        domain=function_args.get("domain"),
                    )
                else:
                    function_response = function_to_call(
                        input=input_param,
                    )
                function_responses.append(
                    {   "input": input_param,
                        "name": function_name,
                        "content": function_response
                    }
                )
        
        return function_responses

@dataclass
class OpenAiModel(BaseModel):
    
    timeout: Optional[float] = None
    
    def __post_init__(self):
        self.api_token = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key = self.api_token)


    def generate(self, input : str, **kwargs):
        '''
        input (str) — Input text.

        
        **kwargs:
        model(string, required): ID of the model to use. You can use the List models API to see all of your available models, or see our Model overview for descriptions of them.
        best_of(integer of null, optional, defaults to 1): Generates best_of completions server-side and returns the "best" (the one with the highest log probability per token). Results cannot be streamed
            When used with n, best_of controls the number of candidate completions and n specifies how many to return – best_of must be greater than n
            Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop
        echo(boolean or null, optional, defaults to false): Echo back the prompt in addition to the completion
        frequency_penalty(number or null, optional, default to 0): Number between -2.0 and 2.0. Positive values penalize new tokens based on their existing frequency in the text so far, decreasing the model's likelihood to repeat the same line verbatim.
        logit_bias(map, optional, defaults to null): Modify the likelihood of specified tokens appearing in the completion.
            Accepts a JSON object that maps tokens (specified by their token ID in the GPT tokenizer) to an associated bias value from -100 to 100. You can use this tokenizer tool (which works for both GPT-2 and GPT-3) to convert text to token IDs. 
            Mathematically, the bias is added to the logits generated by the model prior to sampling. The exact effect will vary per model, but values between -1 and 1 should decrease or increase likelihood of selection; values like -100 or 100 should result in a ban or exclusive selection of the relevant token.
            As an example, you can pass {"50256": -100} to prevent the <|endoftext|> token from being generated.
        logprobs(integer or null, optional, defaults to null):   Include the log probabilities on the logprobs most likely tokens, as well the chosen tokens. For example, if logprobs is 5, the API will return a list of the 5 most likely tokens. 
        The API will always return the logprob of the sampled token, so there may be up to logprobs+1 elements in the response.  
            The maximum value for logprobs is 5.
        max_tokens(integer or null, optional, defalut to 16): The maximum number of tokens to generate in the completion.
            The token count of your prompt plus max_tokens cannot exceed the model's context length. Example Python code for counting tokens.
        n(integer or null, optional, defaults to 1): How many completions to generate for each prompt.
            Note: Because this parameter generates many completions, it can quickly consume your token quota. Use carefully and ensure that you have reasonable settings for max_tokens and stop.
            presence_penalty(number or null,Optional, Defaults to 0): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
        presence_penalty(number or null, Optional, Defaults to 0): Number between -2.0 and 2.0. Positive values penalize new tokens based on whether they appear in the text so far, increasing the model's likelihood to talk about new topics.
        seed(integer or null, Optional): If specified, our system will make a best effort to sample deterministically, such that repeated requests with the same seed and parameters should return the same result
            Determinism is not guaranteed, and you should refer to the system_fingerprint response parameter to monitor changes in the backend.
        stop(string / array / null, Optional, Defaults to null): Up to 4 sequences where the API will stop generating further tokens. The returned text will not contain the stop sequence.
        stream(boolean or null,Optional, Defaults to false): Whether to stream back partial progress. If set, tokens will be sent as data-only server-sent events as they become available, with the stream terminated by a data: [DONE] message.
        suffix(string or null,Optional, Defaults to null): The suffix that comes after a completion of inserted text.
        temperature(number or null, Optional, Defaults to 1): What sampling temperature to use, between 0 and 2. Higher values like 0.8 will make the output more random, while lower values like 0.2 will make it more focused and deterministic.
            We generally recommend altering this or top_p but not both.
        top_p(number or null, Optional, Defaults to 1): An alternative to sampling with temperature, called nucleus sampling, where the model considers the results of the tokens with top_p probability mass. So 0.1 means only the tokens comprising the top 10% probability mass are considered.
            We generally recommend altering this or top_p but not both.
        user(string, Optional): A unique identifier representing your end-user, which can help OpenAI to monitor and detect abuse
        
        Returns a completion object, or a sequence of completion objects if the request is streamed.
        
        The completion object
        id(string): A unique identifier for the completion.
        choices(array): The list of completion choices the model generated for the input prompt.
            The properties of element in choices(array):  #note that, I always see the choices has only 1 element!
            finish_reason(string): The reason the model stopped generating tokens. This will be stop if the model hit a natural stop point or a provided stop sequence, length if the maximum number of tokens specified in the request was reached, or content_filter if content was omitted due to a flag from our content filters.
            index(integer)
            logprobs(object or null)
            text(string) => this is the text that the model generate
        created: The Unix timestamp (in seconds) of when the completion was created.
        model: The model used for completion.
        system_fingerprint
        object
        usage
        '''
        response = self.client.completions.create(
            model=self.model,
            prompt=input,
            **kwargs
        )
        
        return response.choices[0].text
    
    async def agenerate(self, input: str, **kwargs):

        response = await self.client.completions.create(
            model=self.model,
            prompt=input,
            **kwargs
        )
        return response.choices[0].text
    