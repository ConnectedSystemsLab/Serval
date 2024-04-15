from argparse import ArgumentParser
import pickle
from xml.etree import ElementTree
from weather import WeatherService
import shapely
from datetime import datetime

def main():
    parser=ArgumentParser()
    parser.add_argument('--image_file_list', type=str, default='data/all_images')
    parser.add_argument('--weather_cache_folder', default='data/weather_cache')
    parser.add_argument('--output_file', type=str, required=True)
    args=parser.parse_args()
    with open(args.image_file_list) as f:
        image_file_list=f.read().splitlines()
    weather_service=WeatherService(args.weather_cache_folder)
    results={}
    for image_file in image_file_list:
        metadata_file=image_file.replace('_3B_AnalyticMS.tif', '_3B_AnalyticMS_metadata.xml')
        metadata=open(metadata_file).read()
        metadata=ElementTree.fromstring(metadata)
        position=metadata.find('.//gml:coordinates', namespaces={'gml': 'http://www.opengis.net/gml'})
        assert position is not None
        position=position.text
        points=[]
        for point in position.split(' '):
            x, y=point.split(',')
            x=float(x)
            y=float(y)
            points.append((x, y))
        boundary=shapely.geometry.Polygon(points)
        center=boundary.centroid
        image_time=metadata.find('.//gml:beginPosition', namespaces={'gml': 'http://www.opengis.net/gml'})
        assert image_time is not None
        image_time=datetime.fromisoformat(image_time.text)
        weather=weather_service.get_weather(center.x, center.y, image_time)
        image_id=image_file.split('/')[-1].split('.')[0]
        image_id=image_id[:-len('_3B_AnalyticMS')]
        assert (metadata_file.split('/')[-1].split('.')[0]).startswith(image_id), f'{metadata_file} does not match {image_file}'
        results[image_id]=weather
    pickle.dump(results, open(args.output_file, "wb"))

if __name__=='__main__':
    main()