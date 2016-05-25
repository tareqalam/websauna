********************
WEBSAUANA CHEATSHEET
********************
==========================================
Database re-structure with blank database
========================================== 

* first delete database
* run these commands::

ws-alembic -c conf/development.ini -x packages=all upgrade head
ws-alembic -c conf/development.ini revision --autogenerate


===============
Model creation
===============

# To create model
---------------

Open ``models.py`` and add::

    from websauna.system.model.meta import Base
    class ModelName(Base):
        #: The table in the database
        __tablename__ = "modelname"
        #: Database primary key for the row (running counter)
        id = Column(Integer, autoincrement=True, primary_key=True)
        #: Publicly exposed non-guessable
        uuid = Column(UUID(as_uuid=True), default=uuid4)
        #: field start here text
        exempleField1 = Column(String(256), default=None)

# To create admin panel to add/edit/delete model data
---------------------------------------------------
- add the following code in ``admins.py``::


    """Admin resource registrations for your app."""

    from websauna.system.admin.modeladmin import model_admin
    from websauna.system.admin.modeladmin import ModelAdmin

    # Import our models
    from . import models


    @model_admin(traverse_id="modelname")
    class ModelNameAdmin(ModelAdmin):
        """Admin resource for question model.

        This class declares a resource for question model admin root folder with listing and add views.
        """

        #: Label as shown in admin
        title = "ModelNames"

        #: Used in admin listings etc. user visible messages
        #: TODO: This mechanism will be phased out in the future versions with gettext or similar replacement for languages that have plulars one, two, many
        singular_name = "modelname"
        plural_name = "modelnames"

        #: Which models this model admin controls
        model = models.ModelName

        class Resource(ModelAdmin.Resource):
            """Declare resource for each individual question.

            View, edit and delete views are registered against this resource.
            """

            def get_title(self):
                """What we show as the item title in question listing."""
                return self.get_object().exampleField1


# To update database
-------------------
run these commands
.. code::

    ws-alembic -c demo.ini -x packages=websauna.egifter upgrade head
    ws-alembic -c demo.ini -x packages=websauna.egifter revision --auto



================
SERVICE Creation
================

# How to create a service:
------------------------

    1. websauna.addonname.interfaces.py add::

        from zope.interface import Interface
        class IExampleService(Interface):
            """IEgifter service

            """

    2. websauna.addonname.exampleservice.py add::

        """Sign up form service."""
        import logging

        from zope.interface import implementer
        from pyramid.response import Response


        from websauna.system.http import Request
        from websauna.addonname.interfaces import IExampleService
        
        logger = logging.getLogger(__name__)

        @implementer(IExampleService)
        class ExampleService:
            """example service
            """

            def __init__(self, request: Request):
                self.request = request

            def service_method_one(self) -> Response:
                """example service method."""
                request = self.request
                var1 = request.registry.settings.get("some.variable.from.ini") 
                var2 = request.registry.settings.get("some.variable2.from.ini")
                # do whatever and construct data
                data = 'something with var1 and 2'
                return data


# How to call service:
--------------------
    1. first add in websauna.addonname.utils.py::

        from websauna.addonname.interfaces import IExampleService
        from pyramid.interfaces import IRequest


        def get_example_service(request: IRequest) -> IExampleService:
            assert IRequest.providedBy(request)
            return request.registry.queryAdapter(request, IExampleService)
    2. then in your view method (in `views.py`)::
        
        import websauna.addonname

        @simple_route("/example-call-service", route_name="example_call_service", renderer='addoname/example-call-service.html')
        def example_call_service(request: Request):
            egifter_service = websauna.addonname.utils.get_example_service(request)
            result = egifter_service.service_method_one()
            return result

================
HOW TO ADD TESTS
================

# Prerequisetes in virtualenv
-----------------------------

Install these in your virtualenv::

    pip install -U pytest
    pip install -U pytest-splinter
    pip install -U webtest

# To add a test
---------------
    * in you tests folder inside addon in our example inside websauna.addonname/websauna/addonname/tests add a test file 'test_something.py'
    * inside `test_something.py` add this code::

        def test_egifter_service_get_brands(web_server:str, browser:DriverAPI, dbsession:Session):
            """See that our example view renders correctly.

            This is a functional test. Prepare the test by creating one user in the database. Then try to login as this user by using Splinter test browser.

            :param web_server: Functional web server py.test fixture - this string points to a started web server with test.ini configuration.

            :param browser: A Splinter web browser used to execute the tests. By default ``splinter.driver.webdriver.firefox.WebDriver``, but can be altered with py.test command line options for pytest-splinter.

            :param dbsession: Active SQLAlchemy database session for the test run.
            """

            # Direct Splinter browser to the website
            b = browser
            b.visit(web_server + "/example-view")

            # After login we see a profile link to our profile
            assert b.is_text_present("sometext that is present after loading of page /example-view")

    * then to run the test::

        py.test websauna/egifter/tests --ini test.ini


=======================
HOW TO ADD CELERY TASKS
=======================

# Create `tasks.py` in your addon (for example in websauana.addonname)
----------------------------------------------------------------------
Add the following code as a startup::

    """Timed tasks."""
    import logging
    from websauna.system.task.celery import celery_app as celery
    from websauna.system.task import TransactionalTask

    logger = logging.getLogger(__name__)


    @celery.task(name="your_task_method_name", base=TransactionalTask)
    def your_task_method_name(request):
        logger.info("something ..")
        logger.info("TODO: Need to implement the actual task here")
        logger.info("something..Done")

# Add in your ini for example in `demo.ini`
-------------------------------------------
please notice I have added websauna.addonname.tasks::

    [celery]
    CELERY_ALWAYS_EAGER = true
    CELERY_IMPORTS =
        websauna.system.devop.tasks
        websauna.addonname.tasks


    [celerybeat:your_task_method_name]
    task = your_task_method_name
    type = timedelta
    schedule = {"seconds": 10}


# To run the task
-----------------

command::

    ws-celery beat -A websauna.system.task.celery.celery_app --ini demo.ini


# Then you need to add in ansible so it gets deoloyed in server
---------------------------------------------------------------

Documentation here `<http://websauna.org/docs/narrative/misc/task.html#configuring-celery-to-start-with-supervisor>`_