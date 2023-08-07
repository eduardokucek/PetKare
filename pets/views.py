from django.shortcuts import render
from rest_framework.views import APIView, Request, Response, status
from django.forms.models import model_to_dict
from .models import Pet
from groups.models import Group
from traits.models import Trait
from .serializers import PetSerializer, GroupSerializer, TraitSerializer
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404


class PetView(APIView, PageNumberPagination):
    def get(self, request: Request) -> Response:
        pet_trait = request.query_params.get("trait", None)

        if pet_trait:
            pets_list = Pet.objects.filter(traits__name__iexact=pet_trait)

            result_page = self.paginate_queryset(pets_list, request)

            serializer = PetSerializer(instance=result_page, many=True)

            return self.get_paginated_response(serializer.data)

        pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request)

        serializer = PetSerializer(instance=result_page, many=True)

        return self.get_paginated_response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PetSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        trait_data = serializer.validated_data.pop("traits")

        new_group = Group.objects.filter(
            scientific_name=group_data["scientific_name"]
        ).first()

        if not new_group:
            new_group = Group.objects.create(**group_data)

        pet = Pet.objects.create(
            group=new_group,
            **serializer.validated_data,
        )

        for trait_dict in trait_data:
            new_trait = Trait.objects.filter(name__iexact=trait_dict["name"]).first()

            if not new_trait:
                new_trait = Trait.objects.create(**trait_dict)

            pet.traits.add(new_trait)

        serializer = PetSerializer(instance=pet)

        return Response(serializer.data, status=status.HTTP_201_CREATED)


class PetDetailView(APIView, PageNumberPagination):
    def get(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(instance=pet)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        serializer = PetSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        for keys in serializer.validated_data.keys():
            if keys == "group":
                group_data = serializer.validated_data.pop("group")
                group = Group.objects.filter(
                    scientific_name=group_data["scientific_name"]
                ).first()

                if not group:
                    new_group = Group.objects.create(**group_data)
                    pet.group = new_group
                elif group:
                    pet.group = group

            elif keys == "traits":
                pet.traits.clear()
                trait_data = serializer.validated_data.pop("traits")

                for trait_dict in trait_data:
                    trait = Trait.objects.filter(
                        name__iexact=trait_dict["name"]
                    ).first()

                    if not trait:
                        new_trait = Trait.objects.create(**trait_dict)
                        pet.traits.add(new_trait)
                    elif trait:
                        pet.traits.add(trait)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()

        serializer = PetSerializer(instance=pet)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def delete(self, request: Request, pet_id: int) -> Response:
        try:
            pet = Pet.objects.get(id=pet_id)
        except Pet.DoesNotExist:
            return Response({"detail": "Not found."}, status.HTTP_404_NOT_FOUND)

        pet.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)
