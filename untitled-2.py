from fastapi import FastAPI
import uvicorn

app = FastAPI()

grad = 90
len_step = 0
point = [0, 0]
@app.get('/turn')
def turn(deg:int):
    return grad

@app.get('/step')
def step(len_step:int):
    return len_step

if __name__ == "__main__":
    uvicorn.run("untitled-2:app", host = "127.0.0.1", port = 10007)
