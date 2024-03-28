# The MIT License (MIT)
# Copyright © 2023 Yuma Rao
# Copyright © 2024 Manifold Labs

# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the “Software”), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.

# THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.

import pydantic
import bittensor as bt
import random
from typing import List, Optional

class InferenceeSamplingParams(pydantic.BaseModel):
    '''
    SamplingParams is a pydantic model that represents the sampling parameters for the model
    '''
    seed: int = pydantic.Field(
        default_factory=lambda: random.randint(0, 2**31 - 1),
        title="Seed",
        description="The seed used to generate the output.",
    )

class ChallengeSamplingParams(pydantic.BaseModel):
    '''
    SamplingParams is a pydantic model that represents the sampling parameters for the model
    '''
    seed: int = pydantic.Field(
        default_factory=lambda: random.randint(0, 2**31 - 1),
        title="Seed",
        description="The seed used to generate the output.",
    )



class Inference(bt.Synapse):
    """
    Challenge is a specialized implementation of the `StreamingSynapse` tailored for prompting functionalities within
    the Bittensor network. This class is intended to interact with a streaming response that contains a sequence of tokens,
    which represent prompts or messages in a certain scenario.

    As a developer, when using or extending the `Challenge` class, you should be primarily focused on the structure
    and behavior of the prompts you are working with. The class has been designed to seamlessly handle the streaming,
    decoding, and accumulation of tokens that represent these prompts.

    Attributes:

    - `query` (str): The query to be sent to the Bittensor network. Immutable.

    - `seed` (int): The seed used to generate the output. Immutable.

    - `completion` (str): Stores the processed result of the streaming tokens. As tokens are streamed, decoded, and
                          processed, they are accumulated in the completion attribute. This represents the "final"
                          product or result of the streaming process.
    - `required_hash_fields` (Optional[List[str]]): A list of fields that are required for the hash.


    Note: While you can directly use the `Challenge` class, it's designed to be extensible. Thus, you can create
    subclasses to further customize behavior for specific prompting scenarios or requirements.
    """
    query: str = pydantic.Field(
        ...,
        title="Query",
        description="The query to be sent to the Bittensor network.",
    )

    sampling_params: ChallengeSamplingParams = pydantic.Field(
        ...,
        title="Sampling Params",
        description="The sampling parameters for the TGI model.",
    )
    completion: str = pydantic.Field(
        None,
        title="Completion",
        description="The processed result of the streaming tokens.",
    )

    required_hash_fields: Optional[List[str]] = pydantic.Field(
        default_factory=lambda: ["query", "sampling_params"],
        title="Required Hash Fields",
        description="A list of fields that are required for the hash.",
        allow_mutation=False,
    )


class Challenge(bt.Synapse):
    """
    Challenge is a specialized implementation of the `StreamingSynapse` tailored for prompting functionalities within
    the Bittensor network. This class is intended to interact with a streaming response that contains a sequence of tokens,
    which represent prompts or messages in a certain scenario.

    As a developer, when using or extending the `Challenge` class, you should be primarily focused on the structure
    and behavior of the prompts you are working with. The class has been designed to seamlessly handle the streaming,
    decoding, and accumulation of tokens that represent these prompts.

    Attributes:
    - `query` (str): The query to be sent to the Bittensor network. Immutable.

    - `seed` (int): The seed used to generate the output. Immutable.

    - `completion` (str): Stores the processed result of the streaming tokens. As tokens are streamed, decoded, and
                          processed, they are accumulated in the completion attribute. This represents the "final"
                          product or result of the streaming process.

    - `required_hash_fields` (Optional[List[str]]): A list of fields that are required for the hash.


    Note: While you can directly use the `Challenge` class, it's designed to be extensible. Thus, you can create
    subclasses to further customize behavior for specific prompting scenarios or requirements.
    """
    query: str = pydantic.Field(
        ...,
        title="Query",
        description="The query to be sent to the Bittensor network.",
    )

    sampling_params: ChallengeSamplingParams = pydantic.Field(
        ...,
        title="Sampling Params",
        description="The sampling parameters for the TGI model.",
    )

    completion: str = pydantic.Field(
        None,
        title="Completion",
        description="The processed result of the streaming tokens.",
    )

    required_hash_fields: Optional[List[str]] = pydantic.Field(
        default_factory=lambda: ["query", "sampling_params"],
        title="Required Hash Fields",
        description="A list of fields that are required for the hash.",
        allow_mutation=False,
    )

  