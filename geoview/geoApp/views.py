
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from .forms import DateInput, LastActiveForm
from .models import StaticFigure, RasterMap
from django.db.models import Q
from datetime import datetime
from pathlib import Path

import math
import os
import json
import folium
import geopandas as gpd
from folium import GeoJson
from folium.plugins import MousePosition
from folium.template import Template
from urllib.parse import urlparse, unquote

import openai
import base64

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

def encode_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


min_long_northern_region= 102.144135
max_long_northern_region= 107.464146
min_lat_northern_region= 20.72855
max_lat_northern_region= 23.51667

'''

'''

# Create your views here.
def home(request):
    form = LastActiveForm()
    shp_dir = os.path.join(os.getcwd(), 'media', 'vietnam')
    m = folium.Map(max_bounds = True,location=[16.4667, 107.5833], title='Viet Nam' ,zoom_start=8, max_zoom=12, min_zoom=7,
                   min_lat=min_lat_northern_region, max_lat=max_lat_northern_region,
                   min_lon=min_long_northern_region, max_lon=max_long_northern_region)
    style_dbscl = {'fillColor': "#63a6bc", 'color': "#2f81b5"}
    vietnam = gpd.read_file(os.path.join(shp_dir, 'vnm.shp'))
    vietnam_geojson = vietnam.to_crs("EPSG:4326").to_json()
    GeoJson(vietnam_geojson, name='Vietnam', style_function=lambda x: style_dbscl).add_to(m)
    folium.LayerControl().add_to(m)

    # Cao Bang
    folium.Marker(
        location= [22.6667, 106.2500],
        tooltip="Cao Bằng",
        icon=folium.Icon(color="Red")
    ).add_to(m)

    # Ha Giang
    folium.Marker(
        location= [22.8333, 104.9833],
        tooltip="Hà Giang",
        icon=folium.Icon(color="Red")
    ).add_to(m)

    # Son La
    folium.Marker(
        location= [21.3167, 103.9000],
        tooltip="Sơn La",
        icon=folium.Icon(color="Red")
    ).add_to(m)
    

    formatter = "function(num) {return L.Util.formatNum(num, 3) + ' º ';};"

    MousePosition(
        position="topright",
        separator=" | ",
        empty_string="NaN",
        lng_first=True,
        num_digits=20,
        prefix="Coordinates:",
        lat_formatter=formatter,
        lng_formatter=formatter,
    ).add_to(m)

    popup1 = folium.LatLngPopup()
    m.add_child(popup1)
    
    popup1._template = Template("""
            {% macro script(this, kwargs) %}
                var {{this.get_name()}} = L.popup();
                function latLngPop(e) {
                    {{this.get_name()}}
                        .setLatLng(e.latlng)
                        .setContent("Latitude: " + e.latlng.lat.toFixed(4) +
                                    "<br>Longitude: " + e.latlng.lng.toFixed(4))
                        .openOn({{this._parent.get_name()}});
                        console.log("Latitude:", e.latlng.lat.toFixed(4));
                        console.log("Longitude:", e.latlng.lng.toFixed(4));

                        parent.document.getElementById('latInput').value = e.latlng.lat.toFixed(4);
                        parent.document.getElementById('lngInput').value = e.latlng.lng.toFixed(4);
                        //parent.document.getElementById('coordForm').submit();
                        //parent.document.getElementById('mainForm').submit();
                    }
                {{this._parent.get_name()}}.on('click', latLngPop);
            {% endmacro %}
                                """)

    m = m._repr_html_()
    context = {'my_map': m, 'form': form}
    return render(request, 'geoApp/home.html', context)

#cor_dict = {"Long An": [10.5833, 106.6333], "Hồ Chí Minh": [10.8230, 106.6297], "Đồng Nai": [11.0000, 106.0000], "Bình Dương": [11.1667, 106.6667], "Tây Ninh": [11.3333, 106.1667], "Bến Tre": [10.2333, 106.3833], "An Giang": [10.4667, 105.1667], "Kiên Giang": [10.0333, 105.0667], "Cần Thơ": [10.0333, 105.0667], "Vĩnh Long": [10.2500, 105.9667], "Trà Vinh": [9.9333, 105.9667], "Sóc Trăng": [9.6000, 105.9667], "Bạc Liêu": [9.2833, 105.7500], "Cà Mau": [9.1833, 105.1667]}
cor_dict = {
  "Hà Nội": [21.0333, 105.8500],
  "Hà Giang": [22.8333, 104.9833],
  "Cao Bằng": [22.6667, 106.2500],
  "Bắc Kạn": [22.1333, 105.8333],
  "Tuyên Quang": [21.8167, 105.2167],
  "Lào Cai": [22.4833, 103.9500],
  "Điện Biên": [21.3833, 103.0167],
  "Lai Châu": [22.0000, 103.1667],
  "Sơn La": [21.3167, 103.9000],
  "Yên Bái": [21.7000, 104.8667],
  "Hoà Bình": [20.8133, 105.3383],
  "Thái Nguyên": [21.5928, 105.8442],
  "Lạng Sơn": [21.8478, 106.7578],
  "Quảng Ninh": [21.0167, 107.3000],
  "Bắc Giang": [21.2667, 106.2000],
  "Phú Thọ": [21.3000, 105.2333],
  "Vĩnh Phúc": [21.3600, 105.5500],
  "Bắc Ninh": [21.1833, 106.0500],
  "Hải Dương": [20.9333, 106.3167],
  "Hải Phòng": [20.8667, 106.6833],
  "Hưng Yên": [20.6500, 106.0667],
  "Thái Bình": [20.4461, 106.3422],
  "Hà Nam": [20.5431, 105.9139],
  "Nam Định": [20.4200, 106.1683],
  "Ninh Bình": [20.2500, 105.9667],
  "Thanh Hóa": [19.8075, 105.7764],
  "Nghệ An": [18.6733, 105.6819],
  "Hà Tĩnh": [18.3333, 105.9000],
  "Quảng Bình": [17.4689, 106.6269],
  "Quảng Trị": [16.7500, 107.2000],
  "Thừa Thiên Huế": [16.4667, 107.5833],
  "Đà Nẵng": [16.0678, 108.2208],
  "Quảng Nam": [15.5736, 108.3000],
  "Quảng Ngãi": [15.1167, 108.8000],
  "Bình Định": [13.7667, 109.2167],
  "Phú Yên": [13.0833, 109.2833],
  "Khánh Hòa": [12.2500, 109.1833],
  "Ninh Thuận": [11.5667, 108.9833],
  "Bình Thuận": [10.9333, 108.1000],
  "Kon Tum": [14.3500, 108.0000],
  "Gia Lai": [13.9833, 108.0000],
  "Đắk Lắk": [12.6667, 108.0500],
  "Đắk Nông": [12.0000, 107.6833],
  "Lâm Đồng": [11.9333, 108.4167],
  "Bình Phước": [11.7500, 106.9167],
  "Tây Ninh": [11.3333, 106.1667],
  "Bình Dương": [11.1667, 106.6667],
  "Đồng Nai": [11.0000, 106.0000],
  "Bà Rịa - Vũng Tàu": [10.3333, 107.0667],
  "Hồ Chí Minh": [10.8230, 106.6297],
  "Long An": [10.5833, 106.6333],
  "Tiền Giang": [10.3500, 106.3667],
  "Bến Tre": [10.2333, 106.3833],
  "Trà Vinh": [9.9333, 105.9667],
  "Vĩnh Long": [10.2500, 105.9667],
  "Đồng Tháp": [10.5167, 105.6333],
  "An Giang": [10.4667, 105.1667],
  "Kiên Giang": [10.0333, 105.0667],
  "Cần Thơ": [10.0333, 105.7833],
  "Hậu Giang": [9.7833, 105.4667],
  "Sóc Trăng": [9.6000, 105.9667],
  "Bạc Liêu": [9.2833, 105.7500],
  "Cà Mau": [9.1833, 105.1667]
}

def calculate_distance(lat1, lon1, lat2, lon2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees) using Haversine formula
    """
    # Convert decimal degrees to radians
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Haversine formula
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Radius of earth in kilometers
    r = 6371
    return c * r

def find_nearest_location(input_lat, input_lng, locations_dict):
    """
    Find the nearest location from the dictionary to the input coordinates
    """
    min_distance = float('inf')
    nearest_location = None
    
    for location_name, coords in locations_dict.items():
        lat, lng = coords[0], coords[1]
        distance = calculate_distance(input_lat, input_lng, lat, lng)
        
        if distance < min_distance:
            min_distance = distance
            nearest_location = location_name
    
    return nearest_location, min_distance

# @csrf_exempt
def rev_click(request):
    if request.method == 'POST':
        lat = request.POST.get('lat')
        lng = request.POST.get('lng')
        if lat=="" and lng=="":
            lat,lng = 22.6667, 106.2500  # Default to Cao Bang if no coordinates provided
        print(request.body)

        print(f"Received coordinates: Latitude={lat}, Longitude={lng}")
        # You can process the coordinates as needed here
        # For example, save them to the database or perform some calculations
        form = LastActiveForm(request.POST)
        if form.is_valid():
            start_active = form.cleaned_data['start_active']
            end_active = form.cleaned_data['end_active']
            print(f"Start Active: {start_active}, End Active: {end_active}")
            
            # Store date range in session for use in output view
            request.session['start_active'] = start_active.isoformat() if start_active else None
            request.session['end_active'] = end_active.isoformat() if end_active else None
        else:
            print("Form is not valid")
            # Clear session data if form is invalid
            request.session['start_active'] = None
            request.session['end_active'] = None
        
        nearest_location, min_distance = find_nearest_location(float(lat), float(lng), cor_dict)
        if min_distance > 100:
            nearest_location = "Không có dữ liệu"
        
        return redirect('output', neartest_location=nearest_location)


def output(request, neartest_location=None):
    # Get the nearest location from URL parameter or set default
    figures = []

    exist_raster_map_flag = False
    
    if neartest_location and neartest_location != "Không có dữ liệu":
        # Get date range from session
        start_date_str = request.session.get('start_active')
        end_date_str = request.session.get('end_active')

        # Parse date strings back to date objects
        start_date = None
        end_date = None
        if start_date_str:
            try:
                start_date = datetime.fromisoformat(start_date_str).date()
            except (ValueError, TypeError):
                start_date = None
        if end_date_str:
            try:
                end_date = datetime.fromisoformat(end_date_str).date()
            except (ValueError, TypeError):
                end_date = None
        
        # Filter figures based on region and date range
        if start_date and end_date:
            # Both dates provided - filter by date range
            figures = StaticFigure.objects.filter(
                region=neartest_location,
                date_taken__range=[start_date, end_date]
            ).order_by('-date_taken')

            RasterObject = RasterMap.objects.filter(
                region=neartest_location,
                date_taken__lte=end_date
                ).order_by('-date_taken').first()
            
            image_src = None
            if RasterObject and RasterObject.image:
                exist_raster_map_flag = True
                # prefer filesystem path if file exists on disk
                try:
                    img_path = RasterObject.image.path

                except Exception:
                    img_path = None

                if img_path and os.path.exists(img_path):
                    image_src = img_path
                else:
                    # fall back to absolute URL (so browser will load it)
                    image_src = request.build_absolute_uri(RasterObject.image.url)

                left, bottom, right, top = RasterObject.bounds
                shp_dir = os.path.join(os.getcwd(), 'media', 'cao_bang')
                m = folium.Map(max_bounds = True,location=RasterObject.map_center, title='Region of Interest' ,zoom_start=8, max_zoom=12, min_zoom=7)
                image = folium.raster_layers.ImageOverlay(
                #image=RasterObject.image.url,
                image=image_src,
                bounds=[[bottom, left], [top, right]],
                opacity=0.8,
                interactive=True,
                cross_origin=False,
                )
                style_dbscl = {'fillColor': "#e63306", 'color': "#e65d0e"}
                cao_bang = gpd.read_file(os.path.join(shp_dir, 'cao_bang.shp'))
                cao_bang_geojson = cao_bang.to_crs("EPSG:4326").to_json()
                GeoJson(cao_bang_geojson, name='Cao Bang', style_function=lambda x: style_dbscl).add_to(m)
                image.add_to(m)
                folium.LayerControl().add_to(m)
                
                m = m._repr_html_()

        elif start_date:
            # Only start date provided - filter from start date onwards
            figures = StaticFigure.objects.filter(
                region=neartest_location,
                date_taken__gte=start_date
            ).order_by('-date_taken')
        elif end_date:
            # Only end date provided - filter up to end date
            figures = StaticFigure.objects.filter(
                region=neartest_location,
                date_taken__lte=end_date
            ).order_by('-date_taken')

            

        else:
            # No date range - show all figures for the region
            figures = StaticFigure.objects.filter(
                region=neartest_location
            ).order_by('-date_taken')

    if exist_raster_map_flag:
        context = {
            'neartest_location': neartest_location,
            'figures': figures,
            'figure_count': len(figures),
            'raster_map': m if (neartest_location != "Không có dữ liệu" and end_date) else None,
        'raster_obj': RasterObject if (neartest_location != "Không có dữ liệu" and end_date) else None,
        'color_map': request.build_absolute_uri(RasterObject.colormap.url) if (neartest_location != "Không có dữ liệu" and end_date) else None,
        }
    else:
        context = {
            'neartest_location': neartest_location,
            'figures': figures,
            'figure_count': len(figures),
        }
    return render(request, 'geoApp/output.html', context)
    #return render(request, 'geoApp/overlay_map.html')

client = openai.OpenAI(api_key=os.getenv("OPEN_AI_API_KEY"))

def chatbot_analyze(request):
    image_url = request.GET.get('image')
    preload_image = None
    # local media folder where uploaded figures are stored
    media_folder = os.path.join(os.getcwd(), 'media', 'figures')
    '''
    if image_url:
        # Extract filename from provided image URL/path and map it to local media folder
        parsed = urlparse(image_url)
        path = parsed.path or image_url
        filename = os.path.basename(unquote(path))
        print("Filename extracted:", filename)
        file_on_system = os.path.join(media_folder, filename)
        # keep the original image reference for template rendering
        preload_image = image_url
    '''
    parsed = urlparse(image_url)
    parsed_path = unquote(parsed.path)
    
    filename = os.path.basename(parsed_path)
    #print("joined", os.path.join(Path(os.getcwd()).parents[0], parsed_path))
    print("Filename from parsed path:", filename)
    #filename = os.path.basename(unquote(path)):
    
    file_on_system = os.path.join(media_folder, filename)
    # keep the original image reference for template rendering
    preload_image = image_url

    
    stream = None
    full_response = ""
    # ensure file_on_system is set (may have been populated above from image URL)
    # Do NOT try to open/encode the file yet; do that only when needed and only when file exists.
    print(file_on_system)
    #b64_img = encode_image_base64(file_on_system)

    if request.method == 'POST':
        # Extract message and image URL from incoming request.
        user_message = ''
        image_path_or_url = None

        # If client sent JSON, parse it first
        try:
            if request.content_type and 'application/json' in request.content_type:
                data = json.loads(request.body.decode('utf-8') or '{}')
                user_message = data.get('message') or data.get('question') or ''
                image_path_or_url = data.get('image') or data.get('image_url')
        except Exception:
            # If parsing fails, fall back to form data below
            pass

        # Fall back to form-encoded POST or GET params
        if not user_message:
            user_message = request.POST.get('message', '')
        if not image_path_or_url:
            image_path_or_url = request.POST.get('image') or request.GET.get('image')

        # If image is a relative path (starts with '/'), convert to absolute URL
        if image_path_or_url and image_path_or_url.startswith('/'):
            try:
                image_path_or_url = request.build_absolute_uri(image_path_or_url)
            except Exception:
                # leave as-is if build fails
                pass

        # Call the vision-capable model with the image URL and user question
        try:

            # Prefer a local file if it exists: try to map the provided image path/url to local media
            
            final_image_source = None
            local_candidate = None
            try:
                if image_path_or_url:
                    parsed = urlparse(image_path_or_url)
                    filename_send = os.path.basename(unquote(parsed.path))
                    local_candidate = os.path.join(media_folder, filename_send)
                    if os.path.exists(local_candidate):
                        final_image_source = f"data:image/jpeg;base64,{encode_image_base64(local_candidate)}"
                    else:
                        # not on disk — fall back to using the provided URL directly
                        final_image_source = image_path_or_url
                else:
                    # If no image_path_or_url provided, but a preload image from GET existed, try it
                    if file_on_system and os.path.exists(file_on_system):
                        final_image_source = f"data:image/jpeg;base64,{encode_image_base64(file_on_system)}"
            except Exception as e:
                print("Image path handling error:", e)
                final_image_source = image_path_or_url or None

            
            output = client.responses.create(
               model="gpt-4.1-mini",
               instructions="""You are an expert in satellite remote sensing and geospatial analysis, especially InSAR technique and its application on tracking land subsidence and erosion.
         Answer the question of the user about this topic and refuse to answer if the question is not related to this topic. There is also an image of Digital Elevation Model (DEM) or unwrapped interferogram from Sentinel-1 / Sentinel 2 satellite created using SNAP that the user may ask you about.
         """,
               input=[{
        "role": "user",
        "content": [
            {"type": "input_text", "text": user_message},
            {
                "type": "input_image",
                "image_url": final_image_source,
            },
        ],
    }],
               stream=False,
               temperature=0.3,
               max_output_tokens=500
            )
        except Exception as e:
            # Return JSON error so the frontend can display a helpful message
            return JsonResponse({'message': f'Error creating response: {e}'}, status=500)

        full_response = output.output_text
                
        return JsonResponse({'message': full_response})
    context = {'preload_image': preload_image}
    return render(request, 'geoApp/chatbot.html', context)

def _3d_dem_view(request):
    return render(request, 'geoApp/dem.html')