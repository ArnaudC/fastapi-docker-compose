from sqladmin import Admin, ModelView, BaseView, expose
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from fastapi import FastAPI
from .models import User, Item


# Admin authentication. Use User api to create an admin user. Full doc at https://aminalaee.dev/sqladmin/authentication/
class AdminLoginBackend(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        request.session.update({"token": "..."})
        return True
    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True
    async def authenticate(self, request: Request) -> bool:
        return "token" in request.session

# Admin User
class UserLoginAdmin(ModelView, model=User):
    ## Permissions
    can_create = True  # If the model can create new instances via SQLAdmin. Default value is True.
    can_edit = True  # If the model instances can be edited via SQLAdmin. Default value is True.
    can_delete = True  # If the model instances can be deleted via SQLAdmin. Default value is True.
    can_view_details = True  # If the model instance details can be viewed via SQLAdmin. Default value is True.
    can_export = True  # If the model data can be exported in the list page. Default value is True.
    ## Metadata
    name = "User"  # Display name for this model. Default value is the class name.
    name_plural = "Users"  # Display plural name for this model. Default value is class name + s.
    icon = "fa-solid fa-user"  # Icon to be displayed for this model in the admin. Only FontAwesome names are supported.
    ## List page
    column_list = [User.id, User.email, User.is_active, User.items]  # List of columns or column names to be displayed in the list page.
    # column_exclude_list = []  # List of columns or column names to be excluded in the list page.
    # column_formatters = {User.email: lambda m, a: m.email[:10]}  # Dictionary of column formatters in the list page.
    column_searchable_list = [User.email]  # List of columns or column names to be searchable in the list page.
    column_sortable_list = [User.id]  # List of columns or column names to be sortable in the list page.
    # column_default_sort = [(User.email, True), (User.name, False)]  # Default sorting if no sorting is applied, tuple of (column, is_descending) or list of the tuple for multiple columns.
    # list_query = []  # A SQLAlchemy select expression to use for model list page.
    # count_query = []  # A SQLAlchemy select expression to use for model count.
    # search_query = []  # A method with the signature of (stmt, term) -> stmt which can customize the search query.
    ## Details page
    # column_details_list = [User.id, User.name]  # List of columns or column names to be displayed in the details page.
    # column_details_exclude_list = [User.id]  # List of columns or column names to be excluded in the details page.
    # column_formatters_detail = {User.name: lambda m, a: m.name[:10]}  # Dictionary of column formatters in the details page.
    ## Pagination options
    # page_size = 50  # Default page size in pagination. Default is 10.
    # page_size_options = [25, 50, 100, 200]  # Pagination selector options. Default is [10, 25, 50, 100].
    ## General options
    # column_labels = {User.mail: "Email"}  # A mapping of column labels, used to map column names to new names in all places.
    # column_type_formatters = dict(ModelView.column_type_formatters, date=date_format)  # A mapping of type keys and callable values to format in all places. For example you can add custom date formatter to be used in both list and detail pages.
    # save_as = True  # A boolean to enable "save as new" option when editing an object.
    # save_as_continue = True  # A boolean to control the redirect URL if save_as is enabled.
    ## Form options
    # form =   # Default form to be used for creating or editing the model. Default value is None and form is created dynamically.
    # form_base_class =   # Default base class for creating forms. Default value is wtforms.Form.
    # form_args = dict(name=dict(label="Full name"))  # Dictionary of form field arguments supported by WTForms.
    # form_widget_args = dict(email=dict(readonly=True))  # Dictionary of form widget rendering arguments supported by WTForms.
    # form_columns = [User.name]  # List of model columns to be included in the form. Default is all model columns.
    # form_excluded_columns =   # List of model columns to be excluded from the form.
    # form_overrides = dict(email=wtforms.EmailField)  # Dictionary of form fields to override when creating the form.
    # form_include_pk = True  # Control if primary key column should be included in create/edit forms. Default is False.
    # form_ajax_refs = {"address": { "fields": ("zip_code", "street"), "order_by": ("id",), } }  # Use Ajax with Select2 for loading relationship models async. This is use ful when the related model has a lot of records.
    ## Export options
    # can_export = True  # If the model can be exported. Default value is True.
    # column_export_list = []  # List of columns to include in the export data. Default is all model columns.
    # column_export_exclude_list = []  # List of columns to exclude in the export data.
    # export_max_rows = 0  # Maximum number of rows to be exported. Default value is 0 which means unlimited.
    # export_types = ["csv"]  # List of export types to be enabled. Default value is ["csv"].
    ## Templates
    # list_template = "custom_list.html"  # Template to use for models list page. Default is list.html.
    # create_template = "create.html"  # Template to use for model creation page. Default is create.html.
    # details_template = "details.html"  # Template to use for model details page. Default is details.html.
    # edit_template = "edit.html"  # Template to use for model edit page. Default is edit.html.
    def is_visible(self, request: Request) -> bool:
        return True
    def is_accessible(self, request: Request) -> bool:
        return True

# Admin views
class ItemAdmin(ModelView, model=Item):
    column_list = [Item.id, Item.description, Item.owner, Item.owner_id]

# Admin custom views
class CustomItemView(BaseView):
    name = "Custom Page"
    icon = "fa-solid fa-list"
    @expose("/custom_view_1", methods=["GET"])
    def custom_page(self, request):
        return self.templates.TemplateResponse(f"custom_view_1.html", context={"request": request}, )
    # async def on_model_change(self, data, model, is_created)  # Called before a model was created or updated.
    # async def after_model_change(self)  # Called after a model was created or updated.
    # async def on_model_delete(self, model)  # Called before a model was deleted.
    # async def after_model_delete(self)  # Called after a model was deleted.


# Admin initialization
def init_admin(app: FastAPI, app_name: str, engine) -> Admin:
    authentication_backend = AdminLoginBackend(secret_key="...")
    templates_dir = f"{app_name}/templates_jinja2/admin"
    admin = Admin(app=app, engine=engine, templates_dir=templates_dir, authentication_backend=authentication_backend, title="SqlAdmin Custom 1", base_url="/admin", logo_url=None)
    admin.add_view(UserLoginAdmin)
    admin.add_view(ItemAdmin)
    admin.add_view(CustomItemView)
    return admin
