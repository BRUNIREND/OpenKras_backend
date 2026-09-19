from pydantic import BaseModel, ConfigDict

class CategoryBase(BaseModel):
    name: str
    icon_url: str | None = None

class CategoryCreate(CategoryBase):
    pass

class CategoryDelete(BaseModel):
    id: int
class CategoryRead(CategoryBase):
    id: int
    model_config = ConfigDict(from_attributes=True)