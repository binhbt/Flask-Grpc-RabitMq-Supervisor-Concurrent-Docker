# RUN docker  
docker-compose up --build  
# Htpp server run on port 81  
curl http://o.o.o.o:81/  
See the console log  
# Grpc server run on port 1020 concurrent  
./grpc_cli ls localhost:1020  
./grpc_cli call localhost:1020 Hello/SayHello "name:'Tome'"  