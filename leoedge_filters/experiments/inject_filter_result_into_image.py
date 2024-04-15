import pickle
import argparse
import logging


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--log_file', type=str, default='/dev/null')
    parser.add_argument('--image_file', type=str, default='image.pkl')
    parser.add_argument('--filter_result_file', type=str,
                        default='filter_result.pkl')
    parser.add_argument('--output_file', type=str, default='image_new.pkl')
    parser.add_argument('--ca_id_file', type=str, default='data/all_ca_id')
    parser.add_argument('--port_id_file', type=str, default='data/all_port_id')
    parser.add_argument('--weather_info_file', type=str,
                        default='data/weather_info.pkl')
    args = parser.parse_args()
    logging.basicConfig(
        filename=args.log_file,
        level=logging.INFO,
        format='[%(asctime)s] {%(pathname)s:%(lineno)d} %(name)s: %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    logging.getLogger("Main").info("Loading image")
    with open(args.image_file, "rb") as f:
        images = pickle.load(f)
    logging.getLogger("Main").info("Loading filter result")
    with open(args.filter_result_file, "rb") as f:
        filter_result = pickle.load(f)
    logging.getLogger("Main").info("Loading weather info")
    with open(args.weather_info_file, "rb") as f:
        weather_info = pickle.load(f)
    logging.getLogger("Main").info("Injecting filter result into image")
    ca_ids = open(args.ca_id_file).read().splitlines()
    port_ids = open(args.port_id_file).read().splitlines()
    for image_id in images:
        if image_id in filter_result:
            # fill the missing values
            if "forest" not in filter_result[image_id]:
                filter_result[image_id]["forest"] = [0, 0]
            if "forest_model" not in filter_result[image_id]:
                filter_result[image_id]["forest_model"] = filter_result[image_id]["forest"]
            if "cloud" not in filter_result[image_id]:
                filter_result[image_id]["cloud"] = [0, 0]
            if 'fire' not in filter_result[image_id]:
                filter_result[image_id]["fire"] = [0, 1]
            filter_result[image_id]["vessel"] = [0, 0]
            filter_result[image_id]["california"] = [image_id in ca_ids, 0]
            filter_result[image_id]["port"] = [image_id in port_ids, 0]
            filter_result[image_id]["forest"][1] = 0
            filter_result[image_id]["cloud"][0] = 1-filter_result[image_id]["cloud"][0]

            images[image_id]["filter_result"] = filter_result[image_id]
        else:
            images[image_id]["filter_result"] = {
                "fire": [0, 1],
                "cloud": [0, 1],
                "forest": [0, 0],
                "vessel": [0, 0.5],
                "california": [0, 0],
                "port": [0, 0],
                "forest_model": [0, 0],
            }


        images[image_id]["side_channel"] = {}
        if image_id in weather_info:
            images[image_id]["side_channel"]["cloud"] = weather_info[image_id]
        else:
            images[image_id]["side_channel"]["cloud"] = 0.5
        images[image_id]["filter_result"]["root"] = [1, 0]
    logging.getLogger("Main").info("Saving image")
    with open(args.output_file, "wb") as f:
        pickle.dump(images, f)


if __name__ == "__main__":
    main()
