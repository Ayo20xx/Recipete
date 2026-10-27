from pydantic import BaseModel


class RecipeSummary(BaseModel):
    id: str
    name: str
    image_url: str | None


class RecipeIngredient(BaseModel):
    name: str
    measure: str


class RecipeDetails(RecipeSummary):
    category: str | None
    area: str | None
    instructions: str | None
    source_url: str | None
    ingredients: list[RecipeIngredient]
