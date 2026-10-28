"""SQLModel metadata used by models and Alembic."""

from sqlmodel import SQLModel

# Import models so their tables are registered in SQLModel metadata.
from app.models.notification import Notification
from app.models.recipe_review import RecipeReview
from app.models.saved_recipe import SavedRecipe
from app.models.user import User

metadata = SQLModel.metadata
