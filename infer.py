from num2words import num2words


def inference(context,num):
    
    num_word = num2words(num)

    num_word = num_word.replace('-', ' ')
    # Remove commas
    num_word = num_word.replace(',', '')


    from huggingface_hub import hf_hub_download

    from llama_cpp import Llama


    model_kwargs = {
    "n_ctx":4096,    # Context length to use
    "n_threads":4,   # Number of CPU threads to use
    "n_gpu_layers":40,# Number of model layers to offload to GPU. Set to 0 if only using CPU
    }

    ## Instantiate model from downloaded file
    llm = Llama(model_path='llama-2-7b-chat-finetune-qa-meta.Q4_K_M.gguf', **model_kwargs)

    ## Generation kwargs
    generation_kwargs = {
        "max_tokens":200, # Max number of new tokens to generate
        "stop":["<|endoftext|>", "</s>"], # Text sequences to stop generation on
        "echo":False, # Echo the prompt in the output
        "top_k":1 # This is essentially greedy decoding, since the model will always return the highest-probability token. Set this value > 1 for sampling decoding
    }

    context=context.strip()
    ## Run inference
    prompt = f'''<s>[INST]<<SYS>> You are a one-word answer question generator. Generate {num_word} questions and answers only based on the provided context. 
    Each question should aim to elicit a specific piece of information or understanding from the passage. 
    Each answer should be strictly limited to only one-word.
    There is no word-limit for the questions.
    Tha answers should striclty contain only alphabets.
    Generate in the following format. Question : Answer
    stop generation after "</s>" is encountered.  <</SYS>>
    [context]:{context}
    [/INST] 
    '''
    
    res = llm(prompt, **generation_kwargs) # Res is a dictionary

    ## Unpack and the generated text from the LLM response dictionary and print it
    result=res["choices"][0]["text"]

    print(result)

    lines = result.strip().split('\n')

    # Initialize an empty list to store answer-question pairs
    pairs = []

    # Iterate through each line
    for line in lines:
        # Split the line into question and answer
        question, answer = line.split(' : ')
        # Extract the text after the colon and remove leading/trailing whitespace
        question = question.split('. ')[1]
        # Remove spaces between words in the answer
        answer = ''.join(answer.split())
        # Append the answer-question pair as a sublist to the pairs list
        pairs.append([answer.strip(),question.strip()])

    # Print the list of lists
    print(pairs)

    
    return pairs


#inference("Blood is a vital fluid in our bodies, composed mainly of plasma and various types of cells. Plasma, the liquid part, carries nutrients and waste. Red blood cells transport oxygen, powered by the pigment hemoglobin, giving blood its red color. White blood cells are immune system defenders, combating infections. Platelets aid in clotting, preventing excessive bleeding. Blood vessels, including arteries, veins, and capillaries, distribute blood throughout the body. The heart pumps blood through these vessels, ensuring oxygenation and waste removal. Valves maintain one-way blood flow, generating the heartbeat's characteristic sound. The pulmonary circuit connects the heart and lungs for oxygenation. Pulse, felt in arteries, reflects heartbeats per minute. In the excretory system, waste removal occurs via kidneys, which filter blood, producing urine. Ureters transport urine to the bladder, where it's stored and expelled through the urethra. Dialysis substitutes kidney function when necessary. In plants, transportation happens through osmosis, root hairs increasing surface area for water absorption, and vascular tissues (phloem and xylem) distributing nutrients and water. Transpiration, loss of water vapor through leaves, aids in water absorption and distribution.",5)