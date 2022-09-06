docker build -t rhodie/simple-python .
docker run -it --name simple-python3.7 -v $(pwd):/usr/src/app rhodie/simple-python

python -m unittest -v --locals test_rh_flow_module.py 


