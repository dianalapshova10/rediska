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
    uvicorn.run("app:untitled-2", host = "0.0.0.0", port = 10007)
