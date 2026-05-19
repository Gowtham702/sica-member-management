import logging
from odoo import http,fields
from odoo.http import request
import json
from datetime import date

today = date.today()


_logger = logging.getLogger(__name__)  # Logger for this module

class MovieListAPI(http.Controller):

    @http.route('/api/movie/list', type='http', auth='public', methods=['GET'], csrf=False)
    def get_movie_list(self, **kwargs):
        try:
            movies = request.env['movie.list'].sudo().search([], order='sequence asc')
            today = fields.Date.today()

            grouped_movies = {}

            for m in movies:
                # Since project_type is Char now, use value directly
                project_type_label = m.project_type or "Undefined"

                if project_type_label not in grouped_movies:
                    grouped_movies[project_type_label] = []

                grouped_movies[project_type_label].append({
                    's_no': m.sequence,
                    'date': m.date.strftime('%Y-%m-%d') if m.date else '',
                    'movie_name': m.movie_name,
                    'dop_name': m.dop_name,
                    'production_companies': m.production_companies,
                    'team_members': m.team_member,
                    'project_type': project_type_label,
                    'movie_link': m.movie_link,
                    'channel_name': m.channel_name,
                    'language': m.language,
                    'membership_no': m.membership_no,
                    'grade': m.grade,
                    'release_state': m.release_state,
                    'status': 'Completed' if m.date and m.date <= today else 'Upcoming',
                })

            # Convert dict → list
            result = [
                {
                    'project_type': project_type_label,
                    'movies': movie_list
                }
                for project_type_label, movie_list in grouped_movies.items()
            ]

            return request.make_response(
                json.dumps({'status': 200, 'message': 'Success', 'data': result}),
                headers=[('Content-Type', 'application/json')]
            )

        except Exception as e:
            return request.make_response(
                json.dumps({
                    'status': 500,
                    'message': 'Internal Server Error',
                    'error': str(e)
                }),
                headers=[('Content-Type', 'application/json')]
            )



    # @http.route('/api/movie/list', type='json', auth='public', methods=['GET'], csrf=False)
    # def get_movie_list(self, **kwargs):
    #     try:
    #         _logger.info("API Call: /api/movie/list - Fetching movie list...")
    #         movies = request.env['movie.list'].sudo().search([], order='sequence asc')
    #         _logger.info(f"Total movies fetched: {len(movies)}")
    #         movie_data = []

    #         for movie in movies:
    #             movie_data.append({
    #                 's_no': movie.sequence,
    #                 'date': movie.date.strftime('%Y-%m-%d') if movie.date else '',
    #                 'movie_name': movie.movie_name,
    #                 'dop_name': movie.dop_name,
    #                 'production_companies': movie.production_companies,
    #                 'team_members': movie.team_member,
    #                 'project_type':movie.project_type,
    #                 'movie_link': movie.movie_link,
    #                 'channel_name':movie.channel_name,

    #             })
    #             _logger.debug(f"Movie entry: {movie_data}")

    #         return ({'status': 200, 'message': 'Success', 'data': movie_data})
    #     except Exception as e:
    #         return ({"status":404,"message":f"Error {str(e)}"})