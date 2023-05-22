-- 1. VIEW THE DATASET

Select *
From PortfolioProject..CovidDeaths
order by 3,4

-- There are some NULL values in the continent column. In these cases, 
-- the corresponding location field is actually a continent, NOT a country.

Select *
From PortfolioProject..CovidVaccinations
where continent IS NOT NULL
order by 3,4

-- Select the most relevant data to be explored later.

Select Location, 
       date, 
	   total_cases, 
	   new_cases, 
	   total_deaths, 
	   population
From PortfolioProject..CovidDeaths
order by 1,2


----------------------------------------------------------------------------------


-- 2. TOTAL CASES VS TOTAL DEATHS

-- Show the likelihood of dying if you contract Covid in a given country.

Select Location, 
       date, 
	   total_cases, 
	   total_deaths, 
	   (total_deaths/total_cases)*100 AS DeathPercentage
From PortfolioProject..CovidDeaths
Where Location = 'United States'
order by 1,2


----------------------------------------------------------------------------------


-- 3. TOTAL CASES VS POPULATION

-- Show what percentage of a given country's population contracted Covid.

Select Location, 
       date, 
	   Population, 
	   total_cases, 
	   (total_cases/Population)*100 AS PercentagePopulationInfected
From PortfolioProject..CovidDeaths
Where Location = 'United Kingdom'
order by 1,2

-- Show countries with the highest daily infection rate compared to population

Select Location, 
       Population, 
	   MAX(total_cases) AS HighestInfectionCount, 
	   MAX((total_cases/Population))*100 AS PercentagePopulationInfected
From PortfolioProject..CovidDeaths
group by Location, Population
order by 4 DESC

-- Show countries with the highest daily death counts per population.

Select Location, 
       MAX(CAST(total_deaths AS INT)) AS TotalDeathCount
-- total_deaths was originally a string data type (nvarchar)
-- so must convert to a numeric data type (INT) for aggregate function to work
From PortfolioProject..CovidDeaths
where continent IS NOT NULL
group by Location
order by 2 DESC

-- Show continents with the highest daily death count per population

Select continent, 
       MAX(CAST(total_deaths AS INT)) AS TotalDeathCount
From PortfolioProject..CovidDeaths
where continent IS NOT NULL
group by continent
order by 2 DESC

-- The above is wrong due to the way the data has been structured 
-- (e.g. TotalDeathCount for North America only includes that of United States 
-- which has the highest daily death count for its continent). Instead, see below:

Select location, 
       MAX(CAST(total_deaths AS INT)) AS TotalDeathCount
From PortfolioProject..CovidDeaths
where continent IS NULL
group by location
order by 2 DESC

-- Prove that highest daily death count for North America = 847942.

Select location, 
       MAX(CAST(total_deaths AS INT)) AS TotalDeathCount
From PortfolioProject..CovidDeaths
where continent IS NULL AND location = 'North America'
group by location

Select continent, 
       location, 
	   MAX(CAST(total_deaths AS INT)) AS TotalDeathCount
From PortfolioProject..CovidDeaths
where continent = 'North America'
group by continent, location
order by 3 DESC

Select SUM(CAST(new_deaths AS INT)) AS TotalDeathCount
From PortfolioProject..CovidDeaths
where continent = 'North America'


----------------------------------------------------------------------------------


-- GLOBAL NUMBERS

-- Shows likelihood of dying if you contract Covid in the world at a given date.

Select date, 
       SUM(new_cases) AS TotalCases,
       SUM(CAST(new_deaths AS int)) AS TotalDeaths,
	   (SUM(CAST(new_deaths AS int))/SUM(new_cases))*100 AS DeathPercentage
From PortfolioProject..CovidDeaths
Where continent is not null
Group by date
order by 1,2

--Show the likelihood of dying of Covid anywhere in the world.

Select SUM(new_cases) AS TotalCases,
       SUM(CAST(new_deaths AS int)) AS TotalDeaths,
	   (SUM(CAST(new_deaths AS int))/SUM(new_cases))*100 AS DeathPercentage
From PortfolioProject..CovidDeaths
Where continent is not null


----------------------------------------------------------------------------------


-- POPULATION VS VACCINATIONS

-- Show how many people globally have been vaccinated.

Select dea.continent, 
       dea.location, 
	   dea.date, 
	   dea.population, 
	   vac.new_vaccinations,
	   --ROW_NUMBER() OVER (Partition by dea.location order by 3) AS row_number,
	   SUM(CAST(vac.new_vaccinations AS int)) OVER (Partition by dea.location Order by dea.location, dea.date) AS cum_total_vaccinations
From PortfolioProject..CovidDeaths dea
Join PortfolioProject..CovidVaccinations vac
   On dea.location = vac.location
   and dea.date = vac.date
where dea.continent is not null
order by 2,3


-- USE CTE to calculate values for a new column showing % of vaccinated people 
-- within a country's population by a given date 
-- Why? We need to calculate a previously undefined variable (cumulative population)
-- before we can create this new column; previously undefined variables cannot be
-- declared whilst making a new column in the same query.

With PopvsVac (Continent, Location, Date, Population, new_vaccinations, cum_total_vaccinations)
as 
(
Select dea.continent, 
       dea.location, 
	   dea.date, 
	   dea.population, 
	   vac.new_vaccinations,
	   SUM(CAST(vac.new_vaccinations AS int)) OVER (Partition by dea.location Order by dea.location, dea.date) AS cum_total_vaccinations
From PortfolioProject..CovidDeaths dea
Join PortfolioProject..CovidVaccinations vac
   On dea.location = vac.location
   and dea.date = vac.date
where dea.continent is not null
)
Select Continent, 
       Location, 
	   Date, 
	   Population, 
	   new_vaccinations,
	   cum_total_vaccinations,
	   Round((cum_total_vaccinations/population)*100,2) AS vaccinated_percentage
From PopvsVac

-- Now use TEMP TABLE instead of CTE

Drop Table if exists #PercentagePopulationVaccinated
Create Table #PercentPopulationVaccinated
(
Continent nvarchar(255),
Location nvarchar(255),
Date datetime,
Population numeric,
new_vaccinations numeric,
cum_total_vaccinations numeric
)

Insert into #PercentPopulationVaccinated
Select dea.continent, 
       dea.location, 
	   dea.date, 
	   dea.population, 
	   vac.new_vaccinations,
	   SUM(CAST(vac.new_vaccinations AS int)) OVER (Partition by dea.location Order by dea.location, dea.date)
From PortfolioProject..CovidDeaths dea
Join PortfolioProject..CovidVaccinations vac
   On dea.location = vac.location
   and dea.date = vac.date
where dea.continent is not null

Select *, (cum_total_vaccinations/population)*100 AS vaccinated_percentage
From #PercentPopulationVaccinated