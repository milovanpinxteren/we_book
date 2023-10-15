import os

from django.core.exceptions import ObjectDoesNotExist

from bookingsystem.Classes.PortalClasses.database_updater import DatabaseUpdater
from bookingsystem.models import Courses, UserRestaurantLink, Dishes
from we_book import settings


class MenuUpdater():


    def update_menu(self, request):
        current_user = request.user.id
        restaurant_id = UserRestaurantLink.objects.filter(user_id=current_user).values_list('restaurant_id', flat=True).first()

        for response in request.POST:
            if response != 'csrfmiddlewaretoken':
                parts = response.split('-')
                column_name = parts[0]
                column_value = request.POST[response]
                part_id = parts[1]
                if 'dish' in part_id:
                    row_id = part_id[7:]
                    DatabaseUpdater().update_model_instance(Dishes, restaurant_id, row_id, column_name, column_value)
                elif 'course' in part_id:
                    row_id = part_id[9:]
                    DatabaseUpdater().update_model_instance(Courses, restaurant_id, row_id, column_name, column_value)
        return restaurant_id

    def generate_menu_html(self, restaurant_id):
        print(restaurant_id)
        courses = Courses.objects.filter(restaurant_id=restaurant_id).order_by('course_order')
        # course_dishes = {}
        # for course in courses:
        #     ordered_dishes = course.dishes_set.order_by('dish_order')
        #     ordered_dishes = course.dishes_set.order_by('dish_order')
        #     course_dishes[course] = ordered_dishes

        generated_folder = os.path.join(settings.BASE_DIR, 'bookingsystem/static/menus')
        if not os.path.exists(generated_folder):
            os.mkdir(generated_folder)

        file_path = os.path.join(generated_folder, f'menu_{restaurant_id}.html')

        html_content = "<html><head>"
        html_content += """<meta http-equiv='Content-Security-Policy' content="frame-ancestors 'self' '89.145.161.168;'">"""
        html_content += "</head><body>"

        for course in courses:
            ordered_dishes = course.dishes_set.order_by('dish_order')
            html_content += f"<div><h2>{course.name}</h2>"
            for dish in ordered_dishes:
                html_content += f"<div><h3>{dish.name}</h3>"
                html_content += f"<p>{dish.price}</p></div>"
            html_content += "</div>"
                # Add more dish details here

        html_content += "</body></html>"



        with open(file_path, 'w') as file:
            file.write(html_content)



