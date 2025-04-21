

dataset_path=$1        
model_name=$2          
output_dir=$3          

python main.py \
  --run_name $output_dir \
  --dataset_path $dataset_path \
  --model $model_name \
  --root_dir ./out/logs \
  --port 8000 \
  --level block \
  --verbose
